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
    ) -> dict:
        raise NotImplementedError


class MockLLM(LLM):
    """Deterministic, no-network mock generation used for the hackathon demo."""

    def generate(
        self,
        question: dict,
        chunks: List[dict],
        distractor_pool: Optional[List[dict]] = None,
    ) -> dict:
        distractor_pool = distractor_pool or []
        concept = question.get("concept", "")
        misconception = question.get("misconception_hint") or (
            f"Hoc vien co the dang hieu nham mot phan cua khai niem '{concept}'."
        )

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
            options = {"A": _first_sentence(chunk["text"])}
            letters = ["B", "C", "D"]
            for letter, wrong in zip(letters, wrong_options):
                options[letter] = _first_sentence(wrong["text"])
            # Pad with generic distractors if the pool ran short.
            for letter in letters:
                if letter not in options:
                    options[letter] = "Khong lien quan den doan trich dan nay."
            reinforcement.append(
                {
                    "stem": (
                        f"Theo doan trich [{chunk['id']}], y nao sau day dung "
                        f"nhat ve khai niem '{concept}'?"
                    ),
                    "options": options,
                    "answer": "A",
                    "source_id": chunk["id"],
                }
            )

        confidence = 0.9 if len(cited_chunks) >= 2 else 0.6

        return {
            "explanation": explanation,
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
    ) -> dict:
        raise NotImplementedError("Điền LLM_API_KEY và triển khai")


def _build_prompt(question: dict, chunks: List[dict]) -> str:
    concept = question.get("concept", "")
    chunk_lines = "\n".join(f"[{c['id']}] {c['text']}" for c in chunks)
    return (
        "Ban la tro giang AI cham bai trac nghiem. Dua CHINH XAC vao cac "
        f"doan trich dan sau (khong bia them), hay giai thich hieu nham "
        f"thuong gap ve khai niem '{concept}' va tra ve DUY NHAT mot JSON "
        "object khop schema: {\"explanation\": string, \"citations\": "
        "[{\"id\": string, \"quote\": string (phai la cau nguyen van trong "
        "doan trich)}], \"reinforcement\": [{\"stem\": string, \"options\": "
        "{\"A\": string, \"B\": string, \"C\": string, \"D\": string}, "
        "\"answer\": \"A\"|\"B\"|\"C\"|\"D\", \"source_id\": string}], "
        "\"confidence\": number tu 0 den 1}.\n\n"
        f"Doan trich dan:\n{chunk_lines}"
    )


def _parse_json_text(text: str) -> dict:
    """Best-effort JSON parse -- strips ```json ... ``` fences if present."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
        cleaned = re.sub(r"```\s*$", "", cleaned).strip()
    return json.loads(cleaned)


class GeminiLLM(LLM):
    """Calls the real Gemini REST API. Only reachable when a key is set."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate(
        self,
        question: dict,
        chunks: List[dict],
        distractor_pool: Optional[List[dict]] = None,
    ) -> dict:
        prompt = _build_prompt(question, chunks)
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
