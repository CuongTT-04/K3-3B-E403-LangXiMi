"""Path-mapping tests for service.remediate / service.confirm_hypothesis.

q01, q09, q10, q11 in mock-data/quiz-day01.json are engineered so that,
marked wrong, they deterministically land on happy / low_confidence /
no_grounding respectively -- see the comments in that file and in
retriever.py for the exact keyword-overlap arithmetic.
"""
from __future__ import annotations

import pytest

from app import data, service

LESSONS = data.load_lessons()
LESSONS_BY_ID = data.index_lessons_by_id(LESSONS)
QUIZ = data.load_quiz("day01")


def _wrong_result(qid: str) -> dict:
    return {"qid": qid, "chosen": None, "correct": "", "is_correct": False}


def test_remediate_path_happy_for_matched_source_ids():
    remediation = service.remediate(QUIZ, [_wrong_result("q01")], LESSONS, LESSONS_BY_ID)
    item = remediation["items"][0]
    assert item["path"] == "happy"
    assert item["hypotheses"] == []
    assert item["fallback"] is False
    assert len(item["reinforcement"]) > 0


def test_remediate_path_low_confidence_has_2_hypotheses_and_no_reinforcement():
    remediation = service.remediate(QUIZ, [_wrong_result("q09")], LESSONS, LESSONS_BY_ID)
    item = remediation["items"][0]
    assert item["path"] == "low_confidence"
    assert item["fallback"] is False
    assert len(item["citations"]) > 0
    assert len(item["hypotheses"]) == 2
    assert {h["id"] for h in item["hypotheses"]} == {"h1", "h2"}
    assert item["reinforcement"] == []


def test_remediate_path_no_grounding_for_ungrounded_concept():
    remediation = service.remediate(QUIZ, [_wrong_result("q10")], LESSONS, LESSONS_BY_ID)
    item = remediation["items"][0]
    assert item["path"] == "no_grounding"
    assert item["fallback"] is True
    assert item["citations"] == []
    assert item["hypotheses"] == []


def test_low_conf_min_env_override_moves_the_boundary(monkeypatch):
    # q11 sits at confidence ~0.667. Raising LOW_CONF_MIN above that pushes
    # it from low_confidence into no_grounding.
    monkeypatch.setenv("LOW_CONF_MIN", "0.9")
    remediation = service.remediate(QUIZ, [_wrong_result("q11")], LESSONS, LESSONS_BY_ID)
    item = remediation["items"][0]
    assert item["path"] == "no_grounding"


def test_confirm_hypothesis_returns_happy_item_with_reinforcement():
    item = service.confirm_hypothesis(QUIZ, "q09", "h1", LESSONS, LESSONS_BY_ID)
    assert item["path"] == "happy"
    assert item["hypotheses"] == []
    assert item["fallback"] is False
    assert len(item["reinforcement"]) > 0


def test_confirm_hypothesis_unknown_question_raises_keyerror():
    with pytest.raises(KeyError):
        service.confirm_hypothesis(QUIZ, "qxx-unknown", "h1", LESSONS, LESSONS_BY_ID)
