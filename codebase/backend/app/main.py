"""FastAPI app: quiz -> submit -> remediation, plus the static frontend."""
from __future__ import annotations

import json
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import data, service
from .schemas import (
    AckOut,
    CorrectionIn,
    QuestionOut,
    QuizOut,
    RemediateConfirmIn,
    RemediateIn,
    RemediationItem,
    RemediationOut,
    ResultItem,
    SubmitIn,
    SubmitOut,
    TaTicketIn,
)

app = FastAPI(title="Quiz Remediation MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LESSONS = data.load_lessons()
LESSONS_BY_ID = data.index_lessons_by_id(LESSONS)

# Append-only event log for /api/correction and /api/ta-ticket (R6 signal).
# Gitignored -- see codebase/.gitignore. Module-level so tests can monkeypatch
# these two names to redirect writes into a tmp_path.
RUNTIME_DIR = Path(__file__).resolve().parent.parent / ".runtime"
EVENTS_PATH = RUNTIME_DIR / "events.jsonl"


def _append_event(event: dict) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    record = {"ts": time.time(), **event}
    with open(EVENTS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _load_quiz_or_404(quiz_id: str) -> dict:
    try:
        return data.load_quiz(quiz_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="quiz not found") from exc


def _quiz_out(quiz: dict) -> QuizOut:
    return QuizOut(
        quiz_id=quiz["quiz_id"],
        title=quiz["title"],
        questions=[
            QuestionOut(id=q["id"], stem=q["stem"], options=q["options"])
            for q in quiz["questions"]
        ],
    )


def _score_quiz(quiz: dict, answers: dict) -> list:
    results = []
    for question in quiz["questions"]:
        chosen = answers.get(question["id"])
        correct = question["answer"]
        results.append(
            {
                "qid": question["id"],
                "chosen": chosen,
                "correct": correct,
                "is_correct": chosen == correct,
            }
        )
    return results


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/quiz/{quiz_id}", response_model=QuizOut)
def get_quiz(quiz_id: str):
    quiz = _load_quiz_or_404(quiz_id)
    return _quiz_out(quiz)


@app.post("/api/quiz/{quiz_id}/submit", response_model=SubmitOut)
def submit_quiz(quiz_id: str, body: SubmitIn):
    quiz = _load_quiz_or_404(quiz_id)
    results = _score_quiz(quiz, body.answers)
    score = sum(1 for r in results if r["is_correct"])
    remediation = service.remediate(quiz, results, LESSONS, LESSONS_BY_ID)
    return SubmitOut(
        score=score,
        total=len(results),
        results=[ResultItem(**r) for r in results],
        remediation=RemediationOut(**remediation),
    )


@app.get("/api/transcript/{chunk_id}")
def get_transcript(chunk_id: str):
    chunk = LESSONS_BY_ID.get(chunk_id)
    if chunk is None:
        raise HTTPException(status_code=404, detail="chunk not found")
    return chunk


@app.post("/api/remediate", response_model=RemediationOut)
def post_remediate(body: RemediateIn):
    quiz = _load_quiz_or_404(body.quiz_id)
    question_index = data.index_questions_by_id(quiz)
    results = []
    for qid in body.wrong_question_ids:
        question = question_index.get(qid)
        results.append(
            {
                "qid": qid,
                "chosen": None,
                "correct": question["answer"] if question else "",
                "is_correct": False,
            }
        )
    remediation = service.remediate(quiz, results, LESSONS, LESSONS_BY_ID)
    return RemediationOut(**remediation)


@app.post("/api/remediate/confirm", response_model=RemediationItem)
def post_remediate_confirm(body: RemediateConfirmIn):
    quiz = _load_quiz_or_404(body.quiz_id)
    try:
        item = service.confirm_hypothesis(
            quiz, body.question_id, body.hypothesis_id, LESSONS, LESSONS_BY_ID
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="question not found") from exc
    return RemediationItem(**item)


@app.post("/api/correction", response_model=AckOut)
def post_correction(body: CorrectionIn):
    _append_event({"type": "correction", **body.model_dump()})
    return AckOut()


@app.post("/api/ta-ticket", response_model=AckOut)
def post_ta_ticket(body: TaTicketIn):
    _append_event({"type": "ta_ticket", **body.model_dump()})
    return AckOut()


FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
