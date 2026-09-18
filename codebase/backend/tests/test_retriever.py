import pytest

from app import data
from app.retriever import retrieve, retrieve_with_confidence

LESSONS = data.load_lessons()
LESSONS_BY_ID = data.index_lessons_by_id(LESSONS)


def test_retrieve_prefers_source_ids():
    chunks = retrieve("rag", ["T01-009", "T01-013"], LESSONS_BY_ID, LESSONS)
    assert [c["id"] for c in chunks] == ["T01-009", "T01-013"]


def test_retrieve_falls_back_to_keyword_overlap_when_source_ids_missing():
    chunks = retrieve("tool_calling", ["T99-999"], LESSONS_BY_ID, LESSONS)
    assert len(chunks) > 0
    assert any(c["concept"] == "tool_calling" for c in chunks)


def test_retrieve_returns_empty_for_unknown_concept():
    chunks = retrieve("quantum_computing_basics", [], LESSONS_BY_ID, LESSONS)
    assert chunks == []


def test_retrieve_with_confidence_is_1_when_source_ids_match():
    chunks, confidence = retrieve_with_confidence(
        "rag", ["T01-009", "T01-013"], LESSONS_BY_ID, LESSONS
    )
    assert [c["id"] for c in chunks] == ["T01-009", "T01-013"]
    assert confidence == 1.0


def test_retrieve_with_confidence_is_partial_for_keyword_overlap():
    # "vector_embedding_scaling" shares 2 of its 3 tokens ("vector",
    # "embedding") with T01-011's text (the best match) -- "scaling"
    # appears nowhere in lessons.json, so the top ratio is deterministically
    # 2/3. T01-012 also matches ("vector" only) with a lower score, so it
    # trails behind T01-011 but is still within the top-3 limit.
    chunks, confidence = retrieve_with_confidence(
        "vector_embedding_scaling", ["T99-905", "T99-906"], LESSONS_BY_ID, LESSONS
    )
    assert chunks[0]["id"] == "T01-011"
    assert confidence == pytest.approx(2 / 3)


def test_retrieve_with_confidence_is_0_for_unknown_concept():
    chunks, confidence = retrieve_with_confidence(
        "kubernetes_deployment_pipeline", ["T99-909"], LESSONS_BY_ID, LESSONS
    )
    assert chunks == []
    assert confidence == 0.0
