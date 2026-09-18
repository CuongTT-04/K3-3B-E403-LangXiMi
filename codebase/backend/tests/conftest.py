import pytest

@pytest.fixture(autouse=True)
def force_mock_llm(monkeypatch):
    """Ensure all automated unit tests use MockLLM to stay fast and avoid network calls."""
    monkeypatch.setenv("LLM_MODE", "mock")
