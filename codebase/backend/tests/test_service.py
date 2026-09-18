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


def test_misconception_mentions_chosen_option():
    # q01: correct answer is B ("Chain-of-thought"); learner picked A.
    wrong = {"qid": "q01", "chosen": "A", "correct": "B", "is_correct": False}
    remediation = service.remediate(QUIZ, [wrong], LESSONS, LESSONS_BY_ID)
    item = remediation["items"][0]
    assert "A" in item["misconception"]
    assert "Chain-of-thought" in item["misconception"]
    assert "Zero-shot prompting" in item["misconception"]


def test_reinforcement_answer_position_varies_and_matches_source_chunk():
    from app.llm import _first_sentence

    wrong_results = [
        {"qid": q["id"], "chosen": None, "correct": "", "is_correct": False}
        for q in QUIZ["questions"]
    ]
    remediation = service.remediate(QUIZ, wrong_results, LESSONS, LESSONS_BY_ID)

    answers_seen = set()
    checked_any = False
    for item in remediation["items"]:
        for reinf in item["reinforcement"]:
            checked_any = True
            answers_seen.add(reinf["answer"])
            source_chunk = LESSONS_BY_ID[reinf["source_id"]]
            assert reinf["options"][reinf["answer"]] == _first_sentence(
                source_chunk["text"]
            )

    assert checked_any
    assert len(answers_seen) >= 2


def test_confirm_hypothesis_branches_explanation_by_hypothesis_id():
    item_h1 = service.confirm_hypothesis(QUIZ, "q09", "h1", LESSONS, LESSONS_BY_ID)
    item_h2 = service.confirm_hypothesis(QUIZ, "q09", "h2", LESSONS, LESSONS_BY_ID)

    assert item_h1["path"] == "happy"
    assert item_h2["path"] == "happy"
    assert item_h1["explanation"] != item_h2["explanation"]
    assert item_h1["citations"] == item_h2["citations"]
    assert item_h1["explanation"].startswith(
        "Nguyên nhân bạn xác nhận: nhầm lẫn khái niệm. "
    )
    assert item_h2["explanation"].startswith(
        "Nguyên nhân bạn xác nhận: đọc lướt bỏ sót từ khoá. "
    )
