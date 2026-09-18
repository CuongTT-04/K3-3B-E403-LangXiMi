"""Runs golden-set.json through the real retriever + MockLLM + validator
pipeline (service.remediate) and prints exactly one summary line:

    eval pass=N/M fallback_ok=K/L low_conf_ok=P/Q citations_invalid=0

Usage: python backend/eval/run_eval.py  (run from the codebase/ directory,
or anywhere -- the backend/ folder is added to sys.path below).
"""
from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import data, service  # noqa: E402


def _check_case(case: dict, quiz: dict, lessons_by_id: dict) -> dict:
    """Runs one golden-set case through the pipeline and grades it against
    ``case["expect_path"]`` (happy / low_confidence / no_grounding).

    Returns {"passed", "expect_path", "path_ok", "citations_invalid"}.
    """
    results = [
        {"qid": qid, "chosen": None, "correct": "", "is_correct": False}
        for qid in case["wrong_question_ids"]
    ]
    remediation = service.remediate(quiz, results)
    items = remediation["items"]

    citations_invalid = 0
    for item in items:
        for citation in item["citations"]:
            chunk = lessons_by_id.get(citation["id"])
            if chunk is None or citation["quote"] not in chunk["text"]:
                citations_invalid += 1

    expect_path = case["expect_path"]

    if expect_path == "no_grounding":
        path_ok = all(item["path"] == "no_grounding" for item in items) and all(
            item["citations"] == [] for item in items
        )
        return {
            "passed": path_ok,
            "expect_path": expect_path,
            "path_ok": path_ok,
            "citations_invalid": citations_invalid,
        }

    if expect_path == "low_confidence":
        path_ok = all(
            item["path"] == "low_confidence" and len(item.get("hypotheses", [])) == 2
            for item in items
        )
        return {
            "passed": path_ok,
            "expect_path": expect_path,
            "path_ok": path_ok,
            "citations_invalid": citations_invalid,
        }

    # happy
    all_happy = all(item["path"] == "happy" for item in items)
    concepts_ok = any(item["concept"] in case["expected_concepts"] for item in items)
    cited_ids = {c["id"] for item in items for c in item["citations"]}
    expected_any = set(case["expected_source_ids_any"])
    source_ok = not expected_any or bool(cited_ids & expected_any)
    case_passed = all_happy and concepts_ok and source_ok
    return {
        "passed": case_passed,
        "expect_path": expect_path,
        "path_ok": case_passed,
        "citations_invalid": citations_invalid,
    }


def run_golden_set() -> dict:
    golden = data.load_golden_set()
    quiz = data.load_quiz("day01")
    lessons_by_id = data.index_lessons_by_id(data.load_lessons())

    pass_count = 0
    fallback_total = 0
    fallback_ok_count = 0
    low_conf_total = 0
    low_conf_ok_count = 0
    citations_invalid_total = 0

    for case in golden:
        outcome = _check_case(case, quiz, lessons_by_id)
        citations_invalid_total += outcome["citations_invalid"]
        if outcome["passed"]:
            pass_count += 1
        if outcome["expect_path"] == "no_grounding":
            fallback_total += 1
            if outcome["path_ok"]:
                fallback_ok_count += 1
        elif outcome["expect_path"] == "low_confidence":
            low_conf_total += 1
            if outcome["path_ok"]:
                low_conf_ok_count += 1

    return {
        "pass_count": pass_count,
        "total_cases": len(golden),
        "fallback_ok": fallback_ok_count,
        "fallback_total": fallback_total,
        "low_conf_ok": low_conf_ok_count,
        "low_conf_total": low_conf_total,
        "citations_invalid": citations_invalid_total,
    }


def format_summary(result: dict) -> str:
    return (
        f"eval pass={result['pass_count']}/{result['total_cases']} "
        f"fallback_ok={result['fallback_ok']}/{result['fallback_total']} "
        f"low_conf_ok={result['low_conf_ok']}/{result['low_conf_total']} "
        f"citations_invalid={result['citations_invalid']}"
    )


def main() -> dict:
    for _name in ("stdout", "stderr"):
        stream = getattr(sys, _name)
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    result = run_golden_set()
    print(format_summary(result))
    return result


if __name__ == "__main__":
    main()
