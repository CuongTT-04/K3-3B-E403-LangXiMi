"""Glues retriever + LLM + validator into the remediation pipeline.

Only wrong answers are processed. Every wrong answer lands on exactly one of
3 experience paths, decided by retrieval confidence (see plan.md §2):

- ``happy``: confidence >= HIGH_CONF_MIN -- full diagnosis + citations +
  reinforcement quiz, shown straight away.
- ``low_confidence``: LOW_CONF_MIN <= confidence < HIGH_CONF_MIN -- citations
  exist but the model isn't sure enough; the learner is asked to confirm one
  of 2 hypotheses (``POST /api/remediate/confirm``) before reinforcement is
  unlocked.
- ``no_grounding``: confidence < LOW_CONF_MIN, chunks == [], or the
  validator rejected the LLM output (fabricated/orphan citation) -- never
  show a shaky citation, degrade to the safe fallback instead.
"""
from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

from . import data, validator
from .llm import get_llm
from .retriever import retrieve_with_confidence

logger = logging.getLogger(__name__)

_UNKNOWN_QUESTION = {
    "id": None,
    "concept": "unknown",
    "source_ids": [],
    "misconception_hint": None,
}


def _high_conf_min() -> float:
    return float(os.environ.get("HIGH_CONF_MIN", "0.75"))


def _low_conf_min() -> float:
    return float(os.environ.get("LOW_CONF_MIN", "0.4"))


def _hypotheses_for(question: dict) -> List[dict]:
    """Exactly 2 candidate root-causes offered on the low_confidence path."""
    concept = question.get("concept", "")
    return [
        {
            "id": "h1",
            "label": (
                f"Chưa phân biệt rõ bản chất của khái niệm '{concept}' với "
                "khái niệm liên quan gần nhất."
            ),
        },
        {
            "id": "h2",
            "label": (
                f"Đọc lướt và bỏ sót từ khoá quan trọng trong câu hỏi về "
                f"'{concept}'."
            ),
        },
    ]


def _remediate_one(
    question: dict, lessons_by_id: Dict[str, dict], lessons: List[dict]
) -> dict:
    chunks, confidence = retrieve_with_confidence(
        question.get("concept", ""),
        question.get("source_ids", []),
        lessons_by_id,
        lessons,
    )

    if not chunks or confidence < _low_conf_min():
        item = validator.fallback_item(question)
        item["path"] = "no_grounding"
        item["hypotheses"] = []
        return item

    llm_instance = get_llm()
    try:
        raw = llm_instance.generate(question, chunks, distractor_pool=lessons)
        item = validator.validate(question, raw, lessons_by_id)
    except Exception as exc:
        logger.warning(
            "LLM call failed for question %s: %s -- degrading to safe fallback",
            question.get("id"),
            exc,
        )
        item = validator.fallback_item(question)
        item["path"] = "no_grounding"
        item["hypotheses"] = []
        return item

    if item["fallback"]:
        item["path"] = "no_grounding"
        item["hypotheses"] = []
        return item

    if confidence >= _high_conf_min():
        item["path"] = "happy"
        item["hypotheses"] = []
    else:
        item["path"] = "low_confidence"
        item["hypotheses"] = _hypotheses_for(question)
        # Reinforcement stays locked until the learner confirms a hypothesis
        # via POST /api/remediate/confirm (see plan.md decision log).
        item["reinforcement"] = []

    return item


def remediate(
    quiz: dict,
    results: List[dict],
    lessons: Optional[List[dict]] = None,
    lessons_by_id: Optional[Dict[str, dict]] = None,
) -> dict:
    if lessons is None:
        lessons = data.load_lessons()
    if lessons_by_id is None:
        lessons_by_id = data.index_lessons_by_id(lessons)

    question_index = data.index_questions_by_id(quiz)
    wrong_results = [r for r in results if not r.get("is_correct", False)]

    if not wrong_results:
        return {"items": [], "skipped": True}

    def _worker(result: dict) -> dict:
        qid = result["qid"]
        question = question_index.get(qid)
        if question is None:
            question = {**_UNKNOWN_QUESTION, "id": qid}
        return _remediate_one(question, lessons_by_id, lessons)

    # Chạy song song qua ThreadPoolExecutor để rút ngắn thời gian xử lý khi sai nhiều câu
    # Giảm từ 80-120 giây (chạy tuần tự) xuống còn ~10-15 giây (chạy song song)
    max_workers = min(5, len(wrong_results))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        items = list(executor.map(_worker, wrong_results))

    return {"items": items, "skipped": False}


def confirm_hypothesis(
    quiz: dict,
    question_id: str,
    hypothesis_id: str,
    lessons: Optional[List[dict]] = None,
    lessons_by_id: Optional[Dict[str, dict]] = None,
) -> dict:
    """Learner picked a low_confidence hypothesis -- return the full item.

    ``hypothesis_id`` is accepted but does not branch the explanation for
    this MVP: confirming either cause is enough signal to unlock the same
    full (happy-shaped) explanation + reinforcement quiz.

    Raises ``KeyError`` if ``question_id`` isn't in ``quiz``.
    """
    if lessons is None:
        lessons = data.load_lessons()
    if lessons_by_id is None:
        lessons_by_id = data.index_lessons_by_id(lessons)

    question_index = data.index_questions_by_id(quiz)
    question = question_index.get(question_id)
    if question is None:
        raise KeyError(question_id)

    chunks, _confidence = retrieve_with_confidence(
        question.get("concept", ""),
        question.get("source_ids", []),
        lessons_by_id,
        lessons,
    )
    if not chunks:
        item = validator.fallback_item(question)
        item["path"] = "no_grounding"
        item["hypotheses"] = []
        return item

    llm_instance = get_llm()
    raw = llm_instance.generate(question, chunks, distractor_pool=lessons)
    item = validator.validate(question, raw, lessons_by_id)
    item["path"] = "no_grounding" if item["fallback"] else "happy"
    item["hypotheses"] = []
    return item
