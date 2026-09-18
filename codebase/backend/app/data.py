"""Loads mock-data JSON files and indexes lesson chunks by id.

DATA_DIR is resolved relative to the backend/ folder (this file lives at
backend/app/data.py), never as an absolute path, so the default value in
.env.example (``../mock-data``) points at codebase/mock-data regardless of
the process' current working directory.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parent.parent  # codebase/backend


def _data_dir() -> Path:
    raw = os.environ.get("DATA_DIR", "../mock-data")
    path = Path(raw)
    if not path.is_absolute():
        path = (BACKEND_DIR / path).resolve()
    return path


def _load_json(filename: str):
    file_path = _data_dir() / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_lessons() -> List[dict]:
    return _load_json("lessons.json")


def load_quiz(quiz_id: str = "day01") -> dict:
    quiz = _load_json(f"quiz-{quiz_id}.json")
    if quiz.get("quiz_id") != quiz_id:
        raise FileNotFoundError(f"quiz_id mismatch for {quiz_id}")
    return quiz


def load_golden_set() -> List[dict]:
    return _load_json("golden-set.json")


def index_lessons_by_id(lessons: List[dict]) -> Dict[str, dict]:
    return {chunk["id"]: chunk for chunk in lessons}


def index_questions_by_id(quiz: dict) -> Dict[str, dict]:
    return {q["id"]: q for q in quiz["questions"]}
