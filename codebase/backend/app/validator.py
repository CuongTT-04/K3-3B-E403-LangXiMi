"""Hard gate on LLM output: every citation must be real, every reinforcement
question must point at a citation that was already verified. Any violation
degrades the item to a safe fallback instead of shipping a hallucinated
citation or an orphan reinforcement question.
"""
from __future__ import annotations

from typing import Dict


def _norm(s: str) -> str:
    """Collapse all whitespace runs to a single space for quote comparison."""
    return " ".join(s.split())


def _citation_is_valid(citation: dict, lessons_by_id: Dict[str, dict]) -> bool:
    chunk = lessons_by_id.get(citation.get("id"))
    if chunk is None:
        return False
    return _norm(citation.get("quote", "")) in _norm(chunk["text"])


def _fallback_item(question: dict) -> dict:
    concept = question.get("concept", "")
    lesson_hint = question.get("misconception_hint") or (
        f"khai niem '{concept}'"
    )
    return {
        "question_id": question["id"],
        "concept": concept,
        "misconception": (
            f"Chua du can cu de chan doan chinh xac hieu nham ve '{concept}'."
        ),
        "explanation": (
            f"He thong chua tim duoc doan tai lieu du tin cay cho cau hoi nay. "
            f"Hay xem lai phan bai giang lien quan den khai niem '{concept}'."
        ),
        "citations": [],
        "reinforcement": [],
        "confidence": 0.0,
        "fallback": True,
        "fallback_note": (
            f"Chua du can cu trong bai giang cho '{concept}'. "
            f"Goi y: {lesson_hint}"
        ),
    }


def validate(question: dict, raw_item: dict, lessons_by_id: Dict[str, dict]) -> dict:
    """Validate a raw LLM item against the lesson index.

    Returns a well-formed RemediationItem dict: either the (trusted) raw
    item with fallback=False, or a fallback item if any check fails.
    """
    citations = raw_item.get("citations", [])
    for citation in citations:
        if not _citation_is_valid(citation, lessons_by_id):
            return _fallback_item(question)

    valid_ids = {c["id"] for c in citations}
    for item in raw_item.get("reinforcement", []):
        if item.get("source_id") not in valid_ids:
            return _fallback_item(question)

    raw_misconception = raw_item.get("misconception")
    if isinstance(raw_misconception, str) and raw_misconception.strip():
        misconception = raw_misconception
    else:
        misconception = question.get("misconception_hint") or (
            f"Hieu nham ve khai niem '{question.get('concept', '')}'."
        )

    return {
        "question_id": question["id"],
        "concept": question.get("concept", ""),
        "misconception": misconception,
        "explanation": raw_item.get("explanation", ""),
        "citations": citations,
        "reinforcement": raw_item.get("reinforcement", []),
        "confidence": raw_item.get("confidence", 0.0),
        "fallback": False,
        "fallback_note": None,
    }


def fallback_item(question: dict) -> dict:
    """Public entry point used by service.py when retrieval finds nothing."""
    return _fallback_item(question)
