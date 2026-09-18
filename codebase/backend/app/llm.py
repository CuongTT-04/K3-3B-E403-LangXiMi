"""LLM interface. ``generate`` never calls the network unless LLM_MODE=gemini.

MockLLM builds a deterministic explanation + reinforcement questions purely
from the retrieved chunks (no API key needed). GeminiLLM calls the real
Gemini REST API via ``httpx`` when ``LLM_MODE=gemini`` and ``GEMINI_API_KEY``
is set; tests mock ``httpx.Client.post`` and never touch the network. If the
key is missing, ``get_llm`` logs a warning and silently falls back to
MockLLM so the demo never breaks for lack of a key. RealLLM is a documented
stub kept for a future non-Gemini provider.

Google's free tier caps each Gemini model at 20 requests/day. ``GeminiLLM``
therefore rotates across a list of models (``GEMINI_MODELS``, see
``_resolve_gemini_models``) and only falls back to ``MockLLM`` once every
model in the list has failed. Successful responses are cached on disk
(``backend/.runtime/llm-cache.json`` by default) keyed by prompt version +
question id + chosen answer + retrieved chunk ids, so re-running the eval
(or the demo) never re-spends quota on an input already answered for real.
``STATS`` counts how many items were served by each path (gemini/cache/
mock_fallback) so ``eval/run_eval.py --llm-stats`` can report how many
explanations in a run are backed by a real model call.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

GEMINI_URL_TMPL = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)

# Bump this when _build_prompt's instructions change meaning -- it is part
# of the cache key so a prompt change never serves a stale cached answer.
PROMPT_VERSION = "2"

# Free-tier quota is 20 requests/day PER MODEL, so GeminiLLM rotates across
# several models instead of hammering one until it 429s all day. Order here
# is just a sane default -- override with the GEMINI_MODELS env var.
DEFAULT_GEMINI_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
    "gemini-3.1-flash-lite",
]

BACKEND_DIR = Path(__file__).resolve().parent.parent  # codebase/backend

# Module-level counters so eval/run_eval.py --llm-stats can report how many
# items in a run were answered by a real Gemini call vs. served from the
# disk cache vs. fell all the way back to MockLLM. Never exposed on the
# RemediationItem schema -- these are process-level stats only.
STATS: Dict[str, int] = {"gemini": 0, "cache": 0, "mock_fallback": 0}
LAST_MODEL: Optional[str] = None


def reset_stats() -> None:
    """Zero the module-level provider counters (call at the top of a run)."""
    global LAST_MODEL
    STATS["gemini"] = 0
    STATS["cache"] = 0
    STATS["mock_fallback"] = 0
    LAST_MODEL = None


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
        "string}], \"confidence\": number tu 0 den 1}.\n"
        "Truong \"quote\" PHAI chep NGUYÊN VĂN mot cau trong doan trich dan, "
        "giu nguyen chinh ta ke ca khi thieu dau; \"source_id\" cua moi cau "
        "cung co PHAI la \"id\" cua mot citation da liet ke o tren.\n\n"
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


def _extract_text(parts: List[dict]) -> str:
    """Pick the part that actually has a ``text`` key.

    Gemini 3.x responses can interleave a ``thoughtSignature`` part before
    the actual answer part, so ``parts[0]`` is not reliable any more.
    """
    for part in parts:
        if isinstance(part, dict) and "text" in part:
            return part["text"]
    raise KeyError("no part with a 'text' key in Gemini response")


# ---------------------------------------------------------------------------
# Disk cache: sha1(prompt version + question id + chosen + sorted chunk ids)
# -> raw LLM result dict. Only ever populated with REAL Gemini responses.
# ---------------------------------------------------------------------------

_cache_data: Optional[Dict[str, dict]] = None
_cache_data_path: Optional[Path] = None


def _cache_path() -> Path:
    raw = os.environ.get("LLM_CACHE_PATH", "").strip()
    if raw:
        return Path(raw)
    return BACKEND_DIR / ".runtime" / "llm-cache.json"


def _cache_enabled() -> bool:
    return os.environ.get("LLM_CACHE", "").strip().lower() != "off"


def _load_cache() -> Dict[str, dict]:
    global _cache_data, _cache_data_path
    path = _cache_path()
    if _cache_data is None or _cache_data_path != path:
        _cache_data_path = path
        try:
            with open(path, "r", encoding="utf-8") as f:
                _cache_data = json.load(f)
        except (OSError, json.JSONDecodeError):
            _cache_data = {}
    return _cache_data


def _save_cache(cache: Dict[str, dict]) -> None:
    path = _cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2, sort_keys=True)


def _cache_key(question: dict, chunks: List[dict], chosen: Optional[str]) -> str:
    payload = {
        "v": PROMPT_VERSION,
        "qid": question.get("id"),
        "chosen": chosen,
        "chunks": sorted(c["id"] for c in chunks),
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()


class GeminiLLM(LLM):
    """Calls the real Gemini REST API, rotating across ``models`` on failure.

    ``generate`` never raises. For each model in ``self.models`` (tried in
    order): a timeout retries the SAME model once before moving on; any
    other failure (429/404/503/other HTTP error, or a 200 with unparsable
    JSON) moves to the next model immediately -- no same-model retry. Once
    every model has failed, ``generate`` falls back to ``MockLLM`` with the
    same inputs so the demo never 500s. A model that succeeds is promoted to
    the front of ``self.models`` so the next call on this same instance
    tries it first. Successful (non-cached) results are cached on disk; see
    module docstring. Test (``tests/test_llm_gemini.py``) monkeypatch
    ``httpx.Client.post``, never touching the network.
    """

    _RECOVERABLE_ERRORS = (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError)

    def __init__(self, api_key: str, models):
        self.api_key = api_key
        self.models: List[str] = [models] if isinstance(models, str) else list(models)
        self.last_model: Optional[str] = None

    def _promote(self, model: str) -> None:
        """Move ``model`` to the front of ``self.models`` (in-instance only)."""
        self.models = [model] + [m for m in self.models if m != model]

    def _call_once(
        self, model: str, question: dict, chunks: List[dict], chosen: Optional[str]
    ) -> dict:
        prompt = _build_prompt(question, chunks, chosen)
        url = GEMINI_URL_TMPL.format(model=model)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        }
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(url, params={"key": self.api_key}, json=payload)
            resp.raise_for_status()
            body = resp.json()
        parts = body["candidates"][0]["content"]["parts"]
        text = _extract_text(parts)
        return _parse_json_text(text)

    def _try_model(
        self, model: str, question: dict, chunks: List[dict], chosen: Optional[str]
    ) -> Optional[dict]:
        """Result dict on success, or ``None`` if the caller should move on
        to the next model in the rotation."""
        try:
            return self._call_once(model, question, chunks, chosen)
        except httpx.TimeoutException as exc:
            logger.warning(
                "GeminiLLM: timeout on model %s, retrying once: %s", model, exc
            )
            try:
                return self._call_once(model, question, chunks, chosen)
            except self._RECOVERABLE_ERRORS as exc2:
                logger.warning(
                    "GeminiLLM: model %s failed again after retry (%s), "
                    "switching model", model, exc2
                )
                return None
        except self._RECOVERABLE_ERRORS as exc:
            logger.warning(
                "GeminiLLM: model %s failed (%s), switching model", model, exc
            )
            return None

    def generate(
        self,
        question: dict,
        chunks: List[dict],
        distractor_pool: Optional[List[dict]] = None,
        chosen: Optional[str] = None,
    ) -> dict:
        global LAST_MODEL
        cache_enabled = _cache_enabled()
        if cache_enabled:
            key = _cache_key(question, chunks, chosen)
            cache = _load_cache()
            if key in cache:
                STATS["cache"] += 1
                return dict(cache[key])

        for model in list(self.models):
            result = self._try_model(model, question, chunks, chosen)
            if result is None:
                continue
            self.last_model = model
            LAST_MODEL = model
            self._promote(model)
            STATS["gemini"] += 1
            if cache_enabled:
                cache = _load_cache()
                cache[key] = result
                _save_cache(cache)
            return result

        logger.warning(
            "GeminiLLM: all %d model(s) exhausted, falling back to MockLLM",
            len(self.models),
        )
        STATS["mock_fallback"] += 1
        return MockLLM().generate(question, chunks, distractor_pool, chosen=chosen)


def _resolve_gemini_models() -> List[str]:
    """``GEMINI_MODELS`` (comma-separated) or ``DEFAULT_GEMINI_MODELS``; if
    ``GEMINI_MODEL`` (legacy single-model env var) is set it is moved to the
    front of the list, de-duplicating."""
    raw = os.environ.get("GEMINI_MODELS", "").strip()
    if raw:
        models = [m.strip() for m in raw.split(",") if m.strip()]
    else:
        models = list(DEFAULT_GEMINI_MODELS)

    single = os.environ.get("GEMINI_MODEL", "").strip()
    if single:
        models = [single] + [m for m in models if m != single]

    seen = set()
    ordered = []
    for m in models:
        if m not in seen:
            seen.add(m)
            ordered.append(m)
    return ordered


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
        return GeminiLLM(api_key, _resolve_gemini_models())
    raise ValueError(f"Unknown LLM_MODE: {mode}")
