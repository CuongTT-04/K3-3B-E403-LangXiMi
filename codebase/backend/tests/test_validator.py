from app import data, validator

LESSONS_BY_ID = data.index_lessons_by_id(data.load_lessons())

QUESTION = {
    "id": "q01",
    "concept": "prompt_engineering",
    "source_ids": ["T01-004"],
    "misconception_hint": "hint",
}


def _real_quote():
    return LESSONS_BY_ID["T01-004"]["text"].split(".")[0].strip() + "."


def test_validator_accepts_valid_item():
    raw = {
        "explanation": "ok",
        "citations": [{"id": "T01-004", "quote": _real_quote()}],
        "reinforcement": [
            {
                "stem": "s",
                "options": {"A": "x", "B": "y", "C": "z", "D": "w"},
                "answer": "A",
                "source_id": "T01-004",
            }
        ],
        "confidence": 0.9,
    }
    item = validator.validate(QUESTION, raw, LESSONS_BY_ID)
    assert item["fallback"] is False
    assert item["citations"] == raw["citations"]
    assert item["fallback_note"] is None


def test_validator_rejects_citation_with_unknown_id():
    raw = {
        "explanation": "ok",
        "citations": [{"id": "T01-999", "quote": "khong ton tai"}],
        "reinforcement": [],
        "confidence": 0.9,
    }
    item = validator.validate(QUESTION, raw, LESSONS_BY_ID)
    assert item["fallback"] is True
    assert item["citations"] == []
    assert item["reinforcement"] == []
    assert item["fallback_note"] is not None


def test_validator_rejects_citation_with_fabricated_quote():
    raw = {
        "explanation": "ok",
        "citations": [{"id": "T01-004", "quote": "cau nay khong co trong doan trich"}],
        "reinforcement": [],
        "confidence": 0.9,
    }
    item = validator.validate(QUESTION, raw, LESSONS_BY_ID)
    assert item["fallback"] is True


def test_validator_rejects_reinforcement_not_pointing_to_a_citation():
    raw = {
        "explanation": "ok",
        "citations": [{"id": "T01-004", "quote": _real_quote()}],
        "reinforcement": [
            {
                "stem": "s",
                "options": {"A": "x", "B": "y", "C": "z", "D": "w"},
                "answer": "A",
                "source_id": "T01-005",  # not among citations above
            }
        ],
        "confidence": 0.9,
    }
    item = validator.validate(QUESTION, raw, LESSONS_BY_ID)
    assert item["fallback"] is True


def test_fallback_item_has_empty_reinforcement_and_note():
    item = validator.fallback_item(QUESTION)
    assert item["fallback"] is True
    assert item["citations"] == []
    assert item["reinforcement"] == []
    assert item["fallback_note"]
