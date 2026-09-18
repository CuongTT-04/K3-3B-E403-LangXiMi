"""Gemini provider: parses real REST responses but NEVER touches the
network -- httpx.Client.post is monkeypatched in every test here. Every
test also isolates the disk cache to a per-test tmp_path (via LLM_CACHE_PATH)
and resets llm.STATS, so no test reads/writes the real
backend/.runtime/llm-cache.json or leaks counters into another test.
"""
from __future__ import annotations

import pytest
import httpx

from app import llm as llm_module

QUESTION = {"id": "q01", "concept": "rag"}
CHUNKS = [{"id": "T01-009", "text": "RAG la ky thuat truy xuat.", "concept": "rag"}]


@pytest.fixture(autouse=True)
def _isolate_llm_state(tmp_path, monkeypatch):
    """Every test in this file gets its own disk-cache file and fresh STATS."""
    monkeypatch.setenv("LLM_CACHE_PATH", str(tmp_path / "llm-cache.json"))
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


def _fake_gemini_payload(text: str) -> dict:
    return {"candidates": [{"content": {"parts": [{"text": text}]}}]}


def _model_from_url(url: str) -> str:
    return url.split("/models/")[1].split(":")[0]


def test_get_llm_gemini_without_key_falls_back_to_mock(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    instance = llm_module.get_llm()
    assert isinstance(instance, llm_module.MockLLM)


def test_get_llm_gemini_with_key_returns_gemini_llm(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-flash")
    monkeypatch.delenv("GEMINI_MODELS", raising=False)

    instance = llm_module.get_llm()
    assert isinstance(instance, llm_module.GeminiLLM)
    # GEMINI_MODEL (legacy single-model env var) is promoted to the front.
    assert instance.models[0] == "gemini-2.5-flash"


def test_resolve_gemini_models_defaults_and_dedupes(monkeypatch):
    monkeypatch.delenv("GEMINI_MODELS", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    assert llm_module._resolve_gemini_models() == llm_module.DEFAULT_GEMINI_MODELS

    monkeypatch.setenv("GEMINI_MODELS", "a,b,c")
    monkeypatch.setenv("GEMINI_MODEL", "b")
    assert llm_module._resolve_gemini_models() == ["b", "a", "c"]


def test_gemini_llm_generate_parses_json_without_network(monkeypatch):
    raw_json = (
        '{"explanation": "ok", "citations": [], "reinforcement": [], '
        '"confidence": 0.9}'
    )
    payload = _fake_gemini_payload(raw_json)

    def fake_post(self, url, params=None, json=None, **kwargs):
        assert "generativelanguage.googleapis.com" in url
        assert params["key"] == "fake-key"
        return _FakeResponse(payload)

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    instance = llm_module.GeminiLLM("fake-key", "gemini-2.5-flash")
    result = instance.generate(QUESTION, CHUNKS)
    assert result == {
        "explanation": "ok",
        "citations": [],
        "reinforcement": [],
        "confidence": 0.9,
    }
    assert instance.last_model == "gemini-2.5-flash"


def test_gemini_llm_generate_strips_markdown_fences(monkeypatch):
    raw_json = (
        "```json\n"
        '{"explanation": "ok", "citations": [], "reinforcement": [], '
        '"confidence": 0.5}\n'
        "```"
    )
    payload = _fake_gemini_payload(raw_json)

    def fake_post(self, url, params=None, json=None, **kwargs):
        return _FakeResponse(payload)

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    instance = llm_module.GeminiLLM("fake-key", "gemini-2.5-flash")
    result = instance.generate(QUESTION, CHUNKS)
    assert result["confidence"] == 0.5


def _assert_has_remediation_shape(result: dict) -> None:
    assert isinstance(result, dict)
    for key in ("explanation", "citations", "reinforcement", "confidence"):
        assert key in result


def test_gemini_llm_generate_never_raises_on_connection_error(monkeypatch):
    def fake_post(self, url, params=None, json=None, **kwargs):
        raise httpx.ConnectError("boom")

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    instance = llm_module.GeminiLLM("fake-key", "gemini-2.5-flash")
    result = instance.generate(QUESTION, CHUNKS)
    _assert_has_remediation_shape(result)


def test_gemini_llm_generate_never_raises_on_malformed_json_body(monkeypatch):
    payload = _fake_gemini_payload("nay khong phai la JSON hop le {")

    def fake_post(self, url, params=None, json=None, **kwargs):
        return _FakeResponse(payload)

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    instance = llm_module.GeminiLLM("fake-key", "gemini-2.5-flash")
    result = instance.generate(QUESTION, CHUNKS)
    _assert_has_remediation_shape(result)


def test_gemini_llm_rotates_models_on_429_then_503_then_succeeds(monkeypatch):
    """model1 -> 429, model2 -> 503, model3 -> 200: no same-model retry for
    either, result comes from model3, and last_model reflects it."""

    def fake_post(self, url, params=None, json=None, **kwargs):
        model = _model_from_url(url)
        if model == "model1":
            return _FakeResponse(status_code=429)
        if model == "model2":
            return _FakeResponse(status_code=503)
        if model == "model3":
            raw_json = (
                '{"explanation": "from model3", "citations": [], '
                '"reinforcement": [], "confidence": 0.7}'
            )
            return _FakeResponse(_fake_gemini_payload(raw_json))
        raise AssertionError(f"unexpected model in url: {model}")

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    instance = llm_module.GeminiLLM("fake-key", ["model1", "model2", "model3"])
    result = instance.generate(QUESTION, CHUNKS)

    assert result["explanation"] == "from model3"
    assert instance.last_model == "model3"
    assert llm_module.STATS == {"gemini": 1, "cache": 0, "mock_fallback": 0}


def test_gemini_llm_all_models_429_falls_back_to_mock_shape_without_raising(
    monkeypatch,
):
    def fake_post(self, url, params=None, json=None, **kwargs):
        return _FakeResponse(status_code=429)

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    instance = llm_module.GeminiLLM("fake-key", ["model1", "model2", "model3"])
    result = instance.generate(QUESTION, CHUNKS)

    _assert_has_remediation_shape(result)
    assert llm_module.STATS == {"gemini": 0, "cache": 0, "mock_fallback": 1}


def test_gemini_llm_promotes_last_successful_model_to_front(monkeypatch):
    """After model3 succeeds once, the SAME instance tries model3 first on
    its next call (different question -> different cache key -> no hit)."""
    call_log = []

    def fake_post(self, url, params=None, json=None, **kwargs):
        model = _model_from_url(url)
        call_log.append(model)
        if model == "model3":
            raw_json = (
                '{"explanation": "ok", "citations": [], "reinforcement": [], '
                '"confidence": 0.7}'
            )
            return _FakeResponse(_fake_gemini_payload(raw_json))
        return _FakeResponse(status_code=429)

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    instance = llm_module.GeminiLLM("fake-key", ["model1", "model2", "model3"])
    instance.generate({"id": "qA", "concept": "x"}, CHUNKS)
    assert call_log == ["model1", "model2", "model3"]

    call_log.clear()
    instance.generate({"id": "qB", "concept": "x"}, CHUNKS)
    assert call_log[0] == "model3"


def test_gemini_llm_caches_result_and_skips_network_on_second_call(monkeypatch):
    post_calls = []

    def fake_post(self, url, params=None, json=None, **kwargs):
        post_calls.append(url)
        raw_json = (
            '{"explanation": "cached-me", "citations": [], "reinforcement": [], '
            '"confidence": 0.8}'
        )
        return _FakeResponse(_fake_gemini_payload(raw_json))

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    instance = llm_module.GeminiLLM("fake-key", "gemini-2.5-flash")
    first = instance.generate(QUESTION, CHUNKS)
    second = instance.generate(QUESTION, CHUNKS)

    assert len(post_calls) == 1
    assert first == second
    assert llm_module.STATS == {"gemini": 1, "cache": 1, "mock_fallback": 0}


def test_gemini_llm_cache_off_calls_network_every_time(monkeypatch):
    monkeypatch.setenv("LLM_CACHE", "off")
    post_calls = []

    def fake_post(self, url, params=None, json=None, **kwargs):
        post_calls.append(url)
        raw_json = (
            '{"explanation": "no-cache", "citations": [], "reinforcement": [], '
            '"confidence": 0.8}'
        )
        return _FakeResponse(_fake_gemini_payload(raw_json))

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    instance = llm_module.GeminiLLM("fake-key", "gemini-2.5-flash")
    instance.generate(QUESTION, CHUNKS)
    instance.generate(QUESTION, CHUNKS)

    assert len(post_calls) == 2
    assert llm_module.STATS == {"gemini": 2, "cache": 0, "mock_fallback": 0}


def test_gemini_llm_never_caches_mock_fallback(monkeypatch):
    def fake_post(self, url, params=None, json=None, **kwargs):
        return _FakeResponse(status_code=429)

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    instance = llm_module.GeminiLLM("fake-key", ["only-model"])
    instance.generate(QUESTION, CHUNKS)

    cache = llm_module._load_cache()
    assert cache == {}


def test_reset_stats_zeroes_counters_and_last_model(monkeypatch):
    def fake_post(self, url, params=None, json=None, **kwargs):
        raw_json = (
            '{"explanation": "x", "citations": [], "reinforcement": [], '
            '"confidence": 0.5}'
        )
        return _FakeResponse(_fake_gemini_payload(raw_json))

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    instance = llm_module.GeminiLLM("fake-key", "gemini-2.5-flash")
    instance.generate(QUESTION, CHUNKS)
    assert llm_module.STATS["gemini"] == 1
    assert llm_module.LAST_MODEL == "gemini-2.5-flash"

    llm_module.reset_stats()
    assert llm_module.STATS == {"gemini": 0, "cache": 0, "mock_fallback": 0}
    assert llm_module.LAST_MODEL is None
