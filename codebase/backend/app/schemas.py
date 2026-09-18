"""Pydantic contract shared by the API layer.

Naming follows the handoff spec: QuizOut never leaks the answer key,
SubmitIn/SubmitOut wrap grading + remediation, RemediationOut is the
citation-checked explanation/reinforcement bundle for wrong answers.
"""
from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel


class QuestionOut(BaseModel):
    """Question as shown to the learner -- no answer, concept or hints."""

    id: str
    stem: str
    options: Dict[str, str]


class QuizOut(BaseModel):
    quiz_id: str
    title: str
    questions: List[QuestionOut]


class SubmitIn(BaseModel):
    answers: Dict[str, str]


class ResultItem(BaseModel):
    qid: str
    chosen: Optional[str]
    correct: str
    is_correct: bool


class Citation(BaseModel):
    id: str
    quote: str


class ReinforcementItem(BaseModel):
    stem: str
    options: Dict[str, str]
    answer: str
    source_id: str


class Hypothesis(BaseModel):
    """One of exactly two candidate root-causes offered on the low_confidence path."""

    id: str
    label: str


class RemediationItem(BaseModel):
    question_id: str
    concept: str
    misconception: str
    explanation: str
    citations: List[Citation]
    reinforcement: List[ReinforcementItem]
    confidence: float
    fallback: bool
    fallback_note: Optional[str] = None
    # Which of the 4 experience paths this item renders as on the frontend.
    # happy: confidence >= HIGH_CONF_MIN. low_confidence: LOW_CONF_MIN <= confidence
    # < HIGH_CONF_MIN. no_grounding: confidence < LOW_CONF_MIN or chunks == [].
    path: Literal["happy", "low_confidence", "no_grounding"]
    hypotheses: List[Hypothesis] = []


class RemediationOut(BaseModel):
    items: List[RemediationItem]
    skipped: bool


class SubmitOut(BaseModel):
    score: int
    total: int
    results: List[ResultItem]
    remediation: RemediationOut


class RemediateIn(BaseModel):
    """Body for POST /api/remediate."""

    quiz_id: str
    wrong_question_ids: List[str]


class RemediateConfirmIn(BaseModel):
    """Body for POST /api/remediate/confirm -- learner picked a hypothesis."""

    quiz_id: str
    question_id: str
    hypothesis_id: str


class CorrectionIn(BaseModel):
    """Body for POST /api/correction -- learner disputes the AI's verdict."""

    quiz_id: str
    question_id: str
    action: Literal["misclick", "dismiss"]


class TaTicketIn(BaseModel):
    """Body for POST /api/ta-ticket -- learner asks a human TA for help."""

    quiz_id: str
    question_id: str
    note: str


class AckOut(BaseModel):
    status: str = "ok"
