"""Gemini provider: parses real REST responses but NEVER touches the
network -- httpx.Client.post is monkeypatched in every test here.
"""
from __future__ import annotations

import httpx

from app import llm as llm_module

QUESTION = {"id": "q01", "concept": "rag"}
CHUNKS = [{"id": "T01-009", "text": "RAG la ky thuat truy xuat.", "concept": "rag"}]


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def _fake_gemini_payload(text: str) -> dict:
    return {"candidates": [{"content": {"parts": [{"text": text}]}}]}


def test_get_llm_gemini_without_key_falls_back_to_mock(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    instance = llm_module.get_llm()
    assert isinstance(instance, llm_module.MockLLM)


def test_get_llm_gemini_with_key_returns_gemini_llm(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-flash")

    instance = llm_module.get_llm()
    assert isinstance(instance, llm_module.GeminiLLM)
    assert instance.model == "gemini-2.5-flash"


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
