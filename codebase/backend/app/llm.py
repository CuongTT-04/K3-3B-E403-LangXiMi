"""LLM interface. ``generate`` never calls the network unless LLM_MODE is
``gemini``/``chain``/``groq``.

MockLLM builds a deterministic explanation + reinforcement questions purely
from the retrieved chunks (no API key needed). GeminiLLM and GroqLLM call
their real REST APIs via ``httpx``; tests mock ``httpx.Client.post`` and
never touch the network. RealLLM is a documented stub kept for a future
non-OpenAI-compatible provider.

Spec #4 makes Gemini the primary AI provider, with Groq (an OpenAI-compatible
chat completions API) as a SECOND fallback tier when Gemini's quota is
exhausted, and MockLLM as the final safety net so the demo never 500s.
``ChainLLM`` implements this: it tries each provider in order via that
provider's ``_rotate_or_raise`` (which itself rotates across that provider's
own model list -- see ``GEMINI_MODELS``/``GROQ_MODELS`` -- raising
``ProviderExhausted`` once every model in ITS list has failed), and only
falls back to ``MockLLM`` once every provider in the chain is exhausted.
``GeminiLLM.generate()`` keeps its own H01 behavior of silently falling back
to ``MockLLM`` by itself when used standalone (``_rotate_or_raise`` wrapped
in a try/except) so existing standalone callers/tests are unaffected;
``GroqLLM.generate()`` raises ``ProviderExhausted`` directly (it has no
standalone legacy contract to preserve), which is exactly what ``ChainLLM``
needs to move on to the next provider.

Successful responses (Gemini OR Groq) are cached on disk
(``backend/.runtime/llm-cache.json`` by default) keyed by prompt version +
question id + chosen answer + retrieved chunk ids (no provider name in the
key, so a cache entry satisfies either provider), so re-running the eval
(or the demo) never re-spends quota on an input already answered for real.
``STATS`` counts how many items were served by each path (gemini/groq/cache/
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

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Measured limits: 1000 requests/day, 8000 tokens/minute (shared across
# models, unlike Gemini's per-model daily cap). ``llama-3.3-70b-versatile``
# is NOT available; these three text models are. Override with GROQ_MODELS.
DEFAULT_GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
]

BACKEND_DIR = Path(__file__).resolve().parent.parent  # codebase/backend

# Module-level counters so eval/run_eval.py --llm-stats can report how many
# items in a run were answered by a real Gemini/Groq call vs. served from
# the disk cache vs. fell all the way back to MockLLM. Never exposed on the
# RemediationItem schema -- these are process-level stats only.
STATS: Dict[str, int] = {"gemini": 0, "groq": 0, "cache": 0, "mock_fallback": 0}
LAST_MODEL: Optional[str] = None


class ProviderExhausted(Exception):
    """Raised by a provider's ``_rotate_or_raise`` once every model in ITS
    own rotation has failed. ``ChainLLM`` catches this to move on to the
    next provider in the chain; it is never raised out of a provider's
    public ``generate()`` except for ``GroqLLM`` (see module docstring)."""


def reset_stats() -> None:
    """Zero the module-level provider counters (call at the top of a run)."""
    global LAST_MODEL
    STATS["gemini"] = 0
    STATS["groq"] = 0
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
    every model has failed, ``_rotate_or_raise`` raises ``ProviderExhausted``;
    the public ``generate()`` catches that itself and falls back to
    ``MockLLM`` with the same inputs so a standalone (non-chained) caller
    never sees a 500. A model that succeeds is promoted to the front of
    ``self.models`` so the next call on this same instance tries it first.
    Successful (non-cached) results are cached on disk; see module
    docstring. Test (``tests/test_llm_gemini.py``) monkeypatch
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

    def _rotate_or_raise(
        self, question: dict, chunks: List[dict], chosen: Optional[str]
    ) -> dict:
        """Cache check + full model rotation. Raises ``ProviderExhausted``
        (never falls back to Mock itself) once every model has failed --
        callers decide what "exhausted" means for them (see ``generate``
        below and ``ChainLLM``)."""
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

        raise ProviderExhausted(
            f"All {len(self.models)} Gemini model(s) exhausted: {self.models}"
        )

    def generate(
        self,
        question: dict,
        chunks: List[dict],
        distractor_pool: Optional[List[dict]] = None,
        chosen: Optional[str] = None,
    ) -> dict:
        try:
            return self._rotate_or_raise(question, chunks, chosen)
        except ProviderExhausted as exc:
            logger.warning("GeminiLLM: %s -- falling back to MockLLM", exc)
            STATS["mock_fallback"] += 1
            return MockLLM().generate(question, chunks, distractor_pool, chosen=chosen)


class GroqLLM(LLM):
    """Calls the Groq (OpenAI-compatible) chat completions API, rotating
    across ``models`` on failure.

    Unlike ``GeminiLLM``, ANY failure (429/404/5xx/other HTTP error/timeout/
    a 200 with unparsable JSON) moves to the next model immediately -- no
    same-model retry at all, not even for a timeout. Once every model has
    failed, ``generate`` (== ``_rotate_or_raise``) RAISES ``ProviderExhausted``
    instead of falling back to ``MockLLM`` itself -- Groq has no standalone
    legacy contract to preserve, and ``ChainLLM`` is the only intended
    caller, so it needs the raise to know to try the next provider. A model
    that succeeds is promoted to the front of ``self.models``. Successful
    (non-cached) results are cached on disk exactly like Gemini's (same
    cache, same key shape -- no provider name in it). Test
    (``tests/test_llm_groq.py``) monkeypatch ``httpx.Client.post``, never
    touching the network.
    """

    _RECOVERABLE_ERRORS = (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError)

    def __init__(self, api_key: str, models):
        self.api_key = api_key
        self.models: List[str] = [models] if isinstance(models, str) else list(models)
        self.last_model: Optional[str] = None

    def _promote(self, model: str) -> None:
        self.models = [model] + [m for m in self.models if m != model]

    def _call_once(
        self, model: str, question: dict, chunks: List[dict], chosen: Optional[str]
    ) -> dict:
        prompt = _build_prompt(question, chunks, chosen)
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(GROQ_URL, headers=headers, json=payload)
            resp.raise_for_status()
            body = resp.json()
        text = body["choices"][0]["message"]["content"]
        return _parse_json_text(text)

    def _rotate_or_raise(
        self, question: dict, chunks: List[dict], chosen: Optional[str]
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
            try:
                result = self._call_once(model, question, chunks, chosen)
            except self._RECOVERABLE_ERRORS as exc:
                logger.warning(
                    "GroqLLM: model %s failed (%s), switching model", model, exc
                )
                continue
            self.last_model = model
            LAST_MODEL = model
            self._promote(model)
            STATS["groq"] += 1
            if cache_enabled:
                cache = _load_cache()
                cache[key] = result
                _save_cache(cache)
            return result

        raise ProviderExhausted(
            f"All {len(self.models)} Groq model(s) exhausted: {self.models}"
        )

    def generate(
        self,
        question: dict,
        chunks: List[dict],
        distractor_pool: Optional[List[dict]] = None,
        chosen: Optional[str] = None,
    ) -> dict:
        # No self-healing here on purpose -- see class docstring. Only
        # ChainLLM (or a caller that wants this behavior) should call this.
        return self._rotate_or_raise(question, chunks, chosen)


class ChainLLM(LLM):
    """Tries each provider in ``providers`` in order (each of which rotates
    its own model list internally via ``_rotate_or_raise``); a provider that
    raises ``ProviderExhausted`` is skipped in favor of the next one. Falls
    back to ``MockLLM`` only once every provider in the chain has failed.
    Never raises. This is what implements spec #4's "Gemini primary, Groq
    fallback, Mock last resort" order.
    """

    def __init__(self, providers: List[LLM]):
        self.providers = providers

    def generate(
        self,
        question: dict,
        chunks: List[dict],
        distractor_pool: Optional[List[dict]] = None,
        chosen: Optional[str] = None,
    ) -> dict:
        for provider in self.providers:
            try:
                return provider._rotate_or_raise(question, chunks, chosen)
            except ProviderExhausted as exc:
                logger.warning(
                    "ChainLLM: %s exhausted (%s), trying next provider",
                    type(provider).__name__,
                    exc,
                )
                continue

        logger.warning("ChainLLM: every provider exhausted, falling back to MockLLM")
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


def _resolve_groq_models() -> List[str]:
    """``GROQ_MODELS`` (comma-separated) or ``DEFAULT_GROQ_MODELS``; if
    ``GROQ_MODEL`` is set it is moved to the front of the list, de-duping."""
    raw = os.environ.get("GROQ_MODELS", "").strip()
    if raw:
        models = [m.strip() for m in raw.split(",") if m.strip()]
    else:
        models = list(DEFAULT_GROQ_MODELS)

    single = os.environ.get("GROQ_MODEL", "").strip()
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
    if mode in ("gemini", "chain"):
        # "gemini" is the legacy mode name, kept for backward compatibility;
        # it now means "the full provider chain" (spec #4: Gemini primary,
        # Groq fallback, Mock last resort), not "Gemini only".
        providers: List[LLM] = []
        gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if gemini_key:
            providers.append(GeminiLLM(gemini_key, _resolve_gemini_models()))
        groq_key = os.environ.get("GROQ_API_KEY", "").strip()
        if groq_key:
            providers.append(GroqLLM(groq_key, _resolve_groq_models()))
        if not providers:
            logging.warning(
                "LLM_MODE=%s nhung khong co GEMINI_API_KEY/GROQ_API_KEY nao -- "
                "roi ve MockLLM.",
                mode,
            )
            return MockLLM()
        return ChainLLM(providers)
    if mode == "groq":
        groq_key = os.environ.get("GROQ_API_KEY", "").strip()
        if not groq_key:
            logging.warning(
                "LLM_MODE=groq nhung thieu GROQ_API_KEY -- roi ve MockLLM."
            )
            return MockLLM()
        return ChainLLM([GroqLLM(groq_key, _resolve_groq_models())])
    raise ValueError(f"Unknown LLM_MODE: {mode}")
