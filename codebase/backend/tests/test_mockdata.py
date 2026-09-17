import re
from collections import Counter

from app import data

ID_RE = re.compile(r"^T01-\d{3}$")


def test_lessons_schema_valid():
    lessons = data.load_lessons()
    assert len(lessons) >= 30

    ids = [chunk["id"] for chunk in lessons]
    assert len(ids) == len(set(ids)), "chunk ids must be unique"
    for chunk in lessons:
        assert ID_RE.match(chunk["id"])
        assert chunk["lesson"]
        assert chunk["concept"]
        assert len(chunk["text"]) > 0

    concept_counts = Counter(chunk["concept"] for chunk in lessons)
    assert len(concept_counts) >= 4
    for concept, count in concept_counts.items():
        assert count >= 7, f"concept {concept} has only {count} chunks"


def test_quiz_schema_valid():
    quiz = data.load_quiz("day01")
    lessons_by_id = data.index_lessons_by_id(data.load_lessons())

    assert quiz["quiz_id"] == "day01"
    assert len(quiz["questions"]) == 11

    seen_ids = set()
    for q in quiz["questions"]:
        assert q["id"] not in seen_ids
        seen_ids.add(q["id"])
        assert set(q["options"].keys()) == {"A", "B", "C", "D"}
        assert q["answer"] in q["options"]
        assert len(q["source_ids"]) >= 2
        for sid in q["source_ids"]:
            # "T99-" ids are deliberately fake -- used by q09/q10/q11 to force
            # the retriever into its keyword-overlap or empty-result branch
            # so the demo can reach the low_confidence/no_grounding paths.
            assert sid in lessons_by_id or sid.startswith("T99-"), (
                f"{sid} referenced by {q['id']} missing from lessons"
            )


def test_golden_set_schema_valid():
    golden = data.load_golden_set()
    assert len(golden) >= 10

    fallback_cases = [c for c in golden if c["expect_fallback"]]
    assert len(fallback_cases) >= 2

    for case in golden:
        assert case["case_id"]
        assert isinstance(case["wrong_question_ids"], list) and case["wrong_question_ids"]
        assert isinstance(case["expected_concepts"], list)
        assert isinstance(case["expected_source_ids_any"], list)
        assert isinstance(case["expect_fallback"], bool)


def test_golden_set_expect_path_consistent_with_fallback():
    golden = data.load_golden_set()
    valid_paths = {"happy", "low_confidence", "no_grounding"}
    low_conf_cases = [c for c in golden if c["expect_path"] == "low_confidence"]
    assert len(low_conf_cases) >= 2

    for case in golden:
        assert case["expect_path"] in valid_paths
        assert case["expect_fallback"] == (case["expect_path"] == "no_grounding")
