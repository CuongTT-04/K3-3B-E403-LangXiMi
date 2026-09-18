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

BACKEND_DIR = Path(__file__).resolve().parent.parent  # src/backend
load_dotenv()
load_dotenv(BACKEND_DIR / ".env")


def _data_dir() -> Path:
    raw = os.environ.get("DATA_DIR")
    if raw:
        path = Path(raw)
        if path.is_absolute() and path.exists():
            return path
        for base in [BACKEND_DIR, BACKEND_DIR.parent.parent]:
            if (base / path).resolve().exists():
                return (base / path).resolve()
    
    # Ưu tiên thư mục mock-data/ ở root của repository (dữ liệu giả lập an toàn)
    root_mock_data = (BACKEND_DIR.parent.parent / "mock-data").resolve()
    if root_mock_data.exists():
        return root_mock_data

    # Fallback các vị trí khác nếu có
    for candidate in [BACKEND_DIR.parent.parent / "data", BACKEND_DIR / "../mock-data", BACKEND_DIR / "mock-data"]:
        if candidate.resolve().exists():
            return candidate.resolve()
            
    return root_mock_data


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
