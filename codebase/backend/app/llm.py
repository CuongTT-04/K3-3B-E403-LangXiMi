"""LLM interface. ``generate`` never calls the network unless LLM_MODE=gemini.

MockLLM builds a deterministic explanation + reinforcement questions purely
from the retrieved chunks (no API key needed). GeminiLLM calls the real
Gemini REST API via ``httpx`` when ``LLM_MODE=gemini`` and ``GEMINI_API_KEY``
is set; tests mock ``httpx.Client.post`` and never touch the network. If the
key is missing, ``get_llm`` logs a warning and silently falls back to
MockLLM so the demo never breaks for lack of a key. RealLLM is a documented
stub kept for a future non-Gemini provider.
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

GEMINI_URL_TMPL = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)


def _first_sentence(text: str) -> str:
    """Shortest leading sentence of ``text`` -- always a substring of it."""
    match = re.search(r"^[^.]+\.", text)
    return match.group(0).strip() if match else text.strip()


class LLM:
    def generate(
        self,
        question: dict,
        chunks: List[dict],
        distractor_pool: Optional[List[dict]] = None,
        chosen: Optional[str] = None,
    ) -> dict:
        raise NotImplementedError


class MockLLM(LLM):
    """Deterministic, no-network mock generation used for the hackathon demo."""

    def generate(
        self,
        question: dict,
        chunks: List[dict],
        distractor_pool: Optional[List[dict]] = None,
        chosen: Optional[str] = None,
    ) -> dict:
        distractor_pool = distractor_pool or []
        concept = question.get("concept", "")
        misconception_hint = question.get("misconception_hint") or (
            f"Hoc vien co the dang hieu nham mot phan cua khai niem '{concept}'."
        )
        options = question.get("options") or {}
        answer = question.get("answer")
        if chosen and answer and chosen in options and answer in options and chosen != answer:
            misconception = (
                f"Bạn chọn {chosen} ('{options[chosen]}') nhưng đáp án đúng là "
                f"{answer} ('{options[answer]}'). {misconception_hint}"
            )
        else:
            misconception = misconception_hint

        cited_chunks = chunks[:2]
        citations = [
            {"id": chunk["id"], "quote": _first_sentence(chunk["text"])}
            for chunk in cited_chunks
        ]

        explanation_parts = [
            f"Cau hoi nay thuoc khai niem '{concept}'.",
            misconception,
        ]
        explanation_parts.extend(chunk["text"] for chunk in cited_chunks)
        explanation = " ".join(explanation_parts)

        distractors = [
            c for c in distractor_pool if c.get("concept") != concept
        ]

        reinforcement = []
        for i, chunk in enumerate(cited_chunks):
            wrong_options = distractors[i * 2 : i * 2 + 3]
            correct_letter = "ABCD"[sum(ord(c) for c in chunk["id"]) % 4]
            remaining_letters = [
                letter for letter in ["A", "B", "C", "D"] if letter != correct_letter
            ]
            options_out = {correct_letter: _first_sentence(chunk["text"])}
            for letter, wrong in zip(remaining_letters, wrong_options):
                options_out[letter] = _first_sentence(wrong["text"])
            # Pad with generic distractors if the pool ran short.
            for letter in remaining_letters:
                if letter not in options_out:
                    options_out[letter] = "Khong lien quan den doan trich dan nay."
            reinforcement.append(
                {
                    "stem": (
                        f"Theo doan trich [{chunk['id']}], y nao sau day dung "
                        f"nhat ve khai niem '{concept}'?"
                    ),
                    "options": options_out,
                    "answer": correct_letter,
                    "source_id": chunk["id"],
                }
            )

        confidence = 0.9 if len(cited_chunks) >= 2 else 0.6

        return {
            "explanation": explanation,
            "misconception": misconception,
            "citations": citations,
            "reinforcement": reinforcement,
            "confidence": confidence,
        }


class RealLLM(LLM):
    """Stub for a future non-Gemini provider. Never call the network from here."""

    def generate(
        self,
        question: dict,
        chunks: List[dict],
        distractor_pool: Optional[List[dict]] = None,
        chosen: Optional[str] = None,
    ) -> dict:
        raise NotImplementedError("Điền LLM_API_KEY và triển khai")


def _build_prompt(
    question: dict, chunks: List[dict], chosen: Optional[str] = None
) -> str:
    concept = question.get("concept", "")
    stem = question.get("stem", "")
    options = question.get("options") or {}
    answer = question.get("answer", "")
    chunk_lines = "\n".join(f"[{c['id']}] {c['text']}" for c in chunks)
    options_lines = "\n".join(f"{letter}: {text}" for letter, text in options.items())
    chosen_line = (
        f"Phuong an hoc vien da chon: {chosen}\n" if chosen else ""
    )
    question_block = (
        f"Cau hoi: {stem}\n"
        f"Cac phuong an:\n{options_lines}\n"
        f"Dap an dung: {answer}\n"
        f"{chosen_line}"
    )
    return (
        "Ban la tro giang AI cham bai trac nghiem. Dua CHINH XAC vao cac "
        f"doan trich dan sau (khong bia them), hay giai thich hieu nham "
        f"thuong gap ve khai niem '{concept}', chi ro vi sao PHUONG AN HOC "
        "VIEN DA CHON (neu co) la sai, va tra ve DUY NHAT mot JSON "
        "object khop schema: {\"explanation\": string, \"misconception\": "
        "string (giai thich hieu nham dua tren phuong an da chon), "
        "\"citations\": [{\"id\": string, \"quote\": string (phai la cau "
        "nguyen van trong doan trich)}], \"reinforcement\": [{\"stem\": "
        "string, \"options\": {\"A\": string, \"B\": string, \"C\": string, "
        "\"D\": string}, \"answer\": \"A\"|\"B\"|\"C\"|\"D\", \"source_id\": "
        "string}], \"confidence\": number tu 0 den 1}.\n\n"
        f"{question_block}\n"
        f"Doan trich dan:\n{chunk_lines}"
    )


def _parse_json_text(text: str) -> dict:
    """Best-effort JSON parse -- strips ```json ... ``` fences if present."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
        cleaned = re.sub(r"```\s*$", "", cleaned).strip()
    return json.loads(cleaned)


_RETRYABLE_HTTP_STATUS_MIN = 500


def _is_retryable_error(exc: Exception) -> bool:
    """Network timeout or 429/5xx -- worth one retry before giving up."""
    if isinstance(exc, httpx.TimeoutException):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status == 429 or status >= _RETRYABLE_HTTP_STATUS_MIN
    return False


class GeminiLLM(LLM):
    """Calls the real Gemini REST API. Only reachable when a key is set.

    ``generate`` never raises: any HTTP or parse failure retries once (only
    when the failure is a timeout or a 429/5xx status), then falls back to
    ``MockLLM`` with the same inputs so the demo never 500s.
    """

    _RECOVERABLE_ERRORS = (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError)

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def _call_once(
        self, question: dict, chunks: List[dict], chosen: Optional[str]
    ) -> dict:
        prompt = _build_prompt(question, chunks, chosen)
        url = GEMINI_URL_TMPL.format(model=self.model)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        }
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(url, params={"key": self.api_key}, json=payload)
            resp.raise_for_status()
            body = resp.json()
        text = body["candidates"][0]["content"]["parts"][0]["text"]
        return _parse_json_text(text)

    def generate(
        self,
        question: dict,
        chunks: List[dict],
        distractor_pool: Optional[List[dict]] = None,
        chosen: Optional[str] = None,
    ) -> dict:
        try:
            return self._call_once(question, chunks, chosen)
        except self._RECOVERABLE_ERRORS as exc:
            if _is_retryable_error(exc):
                try:
                    return self._call_once(question, chunks, chosen)
                except self._RECOVERABLE_ERRORS as exc2:
                    logger.warning(
                        "GeminiLLM.generate failed after 1 retry: %s", exc2
                    )
                    return MockLLM().generate(
                        question, chunks, distractor_pool, chosen=chosen
                    )
            logger.warning("GeminiLLM.generate failed (no retry): %s", exc)
            return MockLLM().generate(question, chunks, distractor_pool, chosen=chosen)


def get_llm() -> LLM:
    mode = os.environ.get("LLM_MODE", "mock").lower()
    if mode == "mock":
        return MockLLM()
    if mode == "real":
        return RealLLM()
    if mode == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            logging.warning(
                "LLM_MODE=gemini nhung thieu GEMINI_API_KEY -- roi ve MockLLM."
            )
            return MockLLM()
        model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        return GeminiLLM(api_key, model)
    raise ValueError(f"Unknown LLM_MODE: {mode}")
