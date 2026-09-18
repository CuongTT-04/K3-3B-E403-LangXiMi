"""Groq provider (OpenAI-compatible chat completions API) and the
Gemini -> Groq -> Mock provider chain. NEVER touches the network --
httpx.Client.post is monkeypatched in every test here. Every test isolates
the disk cache to a per-test tmp_path (LLM_CACHE_PATH) and resets
llm.STATS, so no test reads/writes the real
backend/.runtime/llm-cache.json or leaks counters/env into another test.
"""
from __future__ import annotations

import pytest
import httpx

from app import llm as llm_module

QUESTION = {"id": "q01", "concept": "rag"}
CHUNKS = [{"id": "T01-009", "text": "RAG la ky thuat truy xuat.", "concept": "rag"}]


@pytest.fixture(autouse=True)
def _isolate_llm_state(tmp_path, monkeypatch):
    """Isolate cache/STATS per test, and strip the legacy single-model env
    vars so the real .env's GEMINI_MODEL/GROQ_MODEL (loaded once into
    os.environ by dotenv, since the test shell never overrides them) can't
    silently get promoted to the front of a test's explicit GEMINI_MODELS/
    GROQ_MODELS list."""
    monkeypatch.setenv("LLM_CACHE_PATH", str(tmp_path / "llm-cache.json"))
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    llm_module.reset_stats()
    yield


class _FakeResponse:
    def __init__(self, payload: dict | None = None, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("POST", "https://example.invalid")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError(
                f"status {self.status_code}", request=request, response=response
            )

    def json(self) -> dict:
        return self._payload


def _fake_groq_payload(text: str) -> dict:
    return {"choices": [{"message": {"content": text}}]}


def _fake_gemini_payload(text: str) -> dict:
    return {"candidates": [{"content": {"parts": [{"text": text}]}}]}


# ---------------------------------------------------------------------------
# Item 1: GroqLLM standalone rotation
# ---------------------------------------------------------------------------


def test_groq_llm_generate_uses_openai_style_endpoint_and_auth_header(monkeypatch):
    raw_json = (
        '{"explanation": "ok", "citations": [], "reinforcement": [], '
        '"confidence": 0.6}'
    )

    def fake_post(self, url, headers=None, json=None, **kwargs):
        assert url == "https://api.groq.com/openai/v1/chat/completions"
        assert headers["Authorization"] == "Bearer fake-groq-key"
        assert json["model"] == "openai/gpt-oss-120b"
        assert json["messages"] == [{"role": "user", "content": llm_module._build_prompt(QUESTION, CHUNKS)}]
        return _FakeResponse(_fake_groq_payload(raw_json))

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    instance = llm_module.GroqLLM("fake-groq-key", "openai/gpt-oss-120b")
    result = instance.generate(QUESTION, CHUNKS)
    assert result["explanation"] == "ok"
    assert instance.last_model == "openai/gpt-oss-120b"


def test_groq_llm_rotates_on_429_then_succeeds_on_second_model(monkeypatch):
    """model 1 -> 429, model 2 -> 200: parses from model 2,
    last_model == default second model (qwen/qwen3.8-27b)."""

    def fake_post(self, url, headers=None, json=None, **kwargs):
        model = json["model"]
        if model == "openai/gpt-oss-120b":
            return _FakeResponse(status_code=429)
        if model == "qwen/qwen3.8-27b":
            raw_json = (
                '{"explanation": "from qwen", "citations": [], '
                '"reinforcement": [], "confidence": 0.5}'
            )
            return _FakeResponse(_fake_groq_payload(raw_json))
        raise AssertionError(f"unexpected model: {model}")

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    instance = llm_module.GroqLLM("fake-groq-key", llm_module.DEFAULT_GROQ_MODELS)
    result = instance.generate(QUESTION, CHUNKS)

    assert result["explanation"] == "from qwen"
    assert instance.last_model == "qwen/qwen3.8-27b"
    assert llm_module.STATS == {"gemini": 0, "groq": 1, "cache": 0, "mock_fallback": 0}


def test_groq_llm_all_models_5xx_raises_provider_exhausted(monkeypatch):
    def fake_post(self, url, headers=None, json=None, **kwargs):
        return _FakeResponse(status_code=503)

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    instance = llm_module.GroqLLM("fake-groq-key", ["model1", "model2", "model3"])
    with pytest.raises(llm_module.ProviderExhausted):
        instance.generate(QUESTION, CHUNKS)

    assert llm_module.STATS == {"gemini": 0, "groq": 0, "cache": 0, "mock_fallback": 0}


def test_groq_llm_never_retries_same_model_on_timeout(monkeypatch):
    """Unlike GeminiLLM, a Groq timeout switches models immediately."""
    calls = []

    def fake_post(self, url, headers=None, json=None, **kwargs):
        model = json["model"]
        calls.append(model)
        if model == "model1":
            raise httpx.TimeoutException("boom")
        raw_json = (
            '{"explanation": "ok", "citations": [], "reinforcement": [], '
            '"confidence": 0.5}'
        )
        return _FakeResponse(_fake_groq_payload(raw_json))

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    instance = llm_module.GroqLLM("fake-groq-key", ["model1", "model2"])
    instance.generate(QUESTION, CHUNKS)

    assert calls == ["model1", "model2"]  # no retry of model1


def test_resolve_groq_models_defaults_and_dedupes(monkeypatch):
    monkeypatch.delenv("GROQ_MODELS", raising=False)
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    assert llm_module._resolve_groq_models() == llm_module.DEFAULT_GROQ_MODELS

    monkeypatch.setenv("GROQ_MODELS", "a,b,c")
    monkeypatch.setenv("GROQ_MODEL", "b")
    assert llm_module._resolve_groq_models() == ["b", "a", "c"]


# ---------------------------------------------------------------------------
# Item 2: get_llm() chain wiring + ChainLLM behavior
# ---------------------------------------------------------------------------


def test_get_llm_no_keys_falls_back_to_mock(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    assert isinstance(llm_module.get_llm(), llm_module.MockLLM)


def test_get_llm_groq_mode_without_key_falls_back_to_mock(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "groq")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    assert isinstance(llm_module.get_llm(), llm_module.MockLLM)


def test_get_llm_groq_mode_with_key_returns_chain_of_one(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "fake-groq-key")

    instance = llm_module.get_llm()
    assert isinstance(instance, llm_module.ChainLLM)
    assert len(instance.providers) == 1
    assert isinstance(instance.providers[0], llm_module.GroqLLM)


def test_get_llm_gemini_mode_with_both_keys_builds_two_provider_chain(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-gemini-key")
    monkeypatch.setenv("GROQ_API_KEY", "fake-groq-key")

    instance = llm_module.get_llm()
    assert isinstance(instance, llm_module.ChainLLM)
    assert [type(p) for p in instance.providers] == [
        llm_module.GeminiLLM,
        llm_module.GroqLLM,
    ]


def test_chain_falls_through_to_groq_when_gemini_exhausted(monkeypatch):
    """Gemini's only model 429s every time; Groq's first model succeeds.
    The chain must return Groq's result, count it under STATS['groq'], and
    never touch mock_fallback."""
    monkeypatch.setenv("LLM_MODE", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-gemini-key")
    monkeypatch.setenv("GEMINI_MODELS", "gemini-only-model")
    monkeypatch.setenv("GROQ_API_KEY", "fake-groq-key")
    monkeypatch.setenv("GROQ_MODELS", "groq-only-model")

    def fake_post(self, url, headers=None, params=None, json=None, **kwargs):
        if "generativelanguage.googleapis.com" in url:
            return _FakeResponse(status_code=429)
        if "api.groq.com" in url:
            raw_json = (
                '{"explanation": "from groq", "citations": [], '
                '"reinforcement": [], "confidence": 0.6}'
            )
            return _FakeResponse(_fake_groq_payload(raw_json))
        raise AssertionError(f"unexpected url: {url}")

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    instance = llm_module.get_llm()
    result = instance.generate(QUESTION, CHUNKS)

    assert result["explanation"] == "from groq"
    assert llm_module.STATS == {"gemini": 0, "groq": 1, "cache": 0, "mock_fallback": 0}


def test_chain_falls_back_to_mock_when_both_providers_exhausted(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-gemini-key")
    monkeypatch.setenv("GEMINI_MODELS", "gemini-only-model")
    monkeypatch.setenv("GROQ_API_KEY", "fake-groq-key")
    monkeypatch.setenv("GROQ_MODELS", "groq-only-model")

    def fake_post(self, url, headers=None, params=None, json=None, **kwargs):
        return _FakeResponse(status_code=429)

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    instance = llm_module.get_llm()
    result = instance.generate(QUESTION, CHUNKS)

    assert isinstance(result, dict)
    for key in ("explanation", "citations", "reinforcement", "confidence"):
        assert key in result
    assert llm_module.STATS == {"gemini": 0, "groq": 0, "cache": 0, "mock_fallback": 1}


def test_chain_cache_is_shared_across_providers_with_no_provider_marker(monkeypatch):
    """A cache entry written by Groq satisfies a later Gemini-first chain
    call for the exact same input, without ever hitting Gemini's network."""
    monkeypatch.setenv("LLM_MODE", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-gemini-key")
    monkeypatch.setenv("GEMINI_MODELS", "gemini-only-model")
    monkeypatch.setenv("GROQ_API_KEY", "fake-groq-key")
    monkeypatch.setenv("GROQ_MODELS", "groq-only-model")

    gemini_calls = []

    def fake_post(self, url, headers=None, params=None, json=None, **kwargs):
        if "generativelanguage.googleapis.com" in url:
            gemini_calls.append(url)
            return _FakeResponse(status_code=429)
        raw_json = (
            '{"explanation": "from groq once", "citations": [], '
            '"reinforcement": [], "confidence": 0.6}'
        )
        return _FakeResponse(_fake_groq_payload(raw_json))

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    first_instance = llm_module.get_llm()
    first = first_instance.generate(QUESTION, CHUNKS)
    assert first["explanation"] == "from groq once"
    assert len(gemini_calls) == 1  # Gemini was tried (and failed) once

    # A brand-new chain instance (as get_llm() would build per-call in
    # service.py) for the SAME input should hit the shared cache before
    # ever trying Gemini again.
    second_instance = llm_module.get_llm()
    second = second_instance.generate(QUESTION, CHUNKS)
    assert second == first
    assert len(gemini_calls) == 1  # no new Gemini attempt
    assert llm_module.STATS == {"gemini": 0, "groq": 1, "cache": 1, "mock_fallback": 0}
