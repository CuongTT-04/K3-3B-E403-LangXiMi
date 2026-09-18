"""Runs golden-set.json through the real retriever + LLM (Mock or Gemini,
per LLM_MODE) + validator pipeline (service.remediate) and prints exactly
one summary line:

    eval pass=N/M fallback_ok=K/L low_conf_ok=P/Q citations_invalid=0

With ``--verbose``, prints one extra line per case before the summary:

    case-XX expect=<path> got=<path1,path2,...> passed=<True/False>

With ``--llm-stats``, resets ``app.llm.STATS`` before the run and prints one
extra line right before the summary:

    llm gemini=<n> groq=<n> cache=<n> mock_fallback=<n> model=<last_model or "-">

``--sleep <seconds>`` (default 0) sleeps between golden-set cases -- useful
with LLM_MODE=gemini to stay under the API's requests-per-minute limit.

Usage: python backend/eval/run_eval.py [--verbose] [--llm-stats]
[--sleep SECONDS]  (run from the codebase/ directory, or anywhere -- the
backend/ folder is added to sys.path below).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import data, llm, service, validator  # noqa: E402


def _check_case(case: dict, quiz: dict, lessons_by_id: dict) -> dict:
    """Runs one golden-set case through the pipeline and grades it.

    Cases with an ``expect_paths`` map (qid -> path) are graded per item:
    every item's actual ``path`` must match its expected path, happy items
    need >=1 citation, no_grounding items need citations == [], and
    low_confidence items need exactly 2 hypotheses.

    Cases without ``expect_paths`` keep the original single-path grading
    (happy / low_confidence / no_grounding applied to every item).

    Returns {"passed", "expect_path", "path_ok", "citations_invalid",
    "paths", and, for mixed cases, "mixed": True + "items": [...]}.
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
            if chunk is None or not validator.quote_matches(
                citation["quote"], chunk["text"]
            ):
                citations_invalid += 1

    expect_path = case["expect_path"]
    expect_paths = case.get("expect_paths")
    paths = [item["path"] for item in items]

    if expect_paths:
        item_checks = []
        path_ok = True
        for item in items:
            qid = item["question_id"]
            expected = expect_paths.get(qid)
            got = item["path"]
            ok = got == expected
            if expected == "happy":
                ok = ok and len(item["citations"]) >= 1
            elif expected == "no_grounding":
                ok = ok and item["citations"] == []
            elif expected == "low_confidence":
                ok = ok and len(item.get("hypotheses", [])) == 2
            item_checks.append({"qid": qid, "expect": expected, "ok": ok})
            path_ok = path_ok and ok
        return {
            "passed": path_ok,
            "expect_path": expect_path,
            "path_ok": path_ok,
            "citations_invalid": citations_invalid,
            "paths": paths,
            "mixed": True,
            "items": item_checks,
        }

    if expect_path == "no_grounding":
        path_ok = all(item["path"] == "no_grounding" for item in items) and all(
            item["citations"] == [] for item in items
        )
        return {
            "passed": path_ok,
            "expect_path": expect_path,
            "path_ok": path_ok,
            "citations_invalid": citations_invalid,
            "paths": paths,
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
            "paths": paths,
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
        "paths": paths,
    }


def run_golden_set(sleep_seconds: float = 0.0) -> dict:
    golden = data.load_golden_set()
    quiz = data.load_quiz("day01")
    lessons_by_id = data.index_lessons_by_id(data.load_lessons())

    pass_count = 0
    fallback_total = 0
    fallback_ok_count = 0
    low_conf_total = 0
    low_conf_ok_count = 0
    citations_invalid_total = 0
    case_results = []

    for case_index, case in enumerate(golden):
        outcome = _check_case(case, quiz, lessons_by_id)
        citations_invalid_total += outcome["citations_invalid"]
        if outcome["passed"]:
            pass_count += 1

        if outcome.get("mixed"):
            # Mixed cases count fallback/low_conf per item, not per case.
            for item_check in outcome["items"]:
                if item_check["expect"] == "no_grounding":
                    fallback_total += 1
                    if item_check["ok"]:
                        fallback_ok_count += 1
                elif item_check["expect"] == "low_confidence":
                    low_conf_total += 1
                    if item_check["ok"]:
                        low_conf_ok_count += 1
        else:
            if outcome["expect_path"] == "no_grounding":
                fallback_total += 1
                if outcome["path_ok"]:
                    fallback_ok_count += 1
            elif outcome["expect_path"] == "low_confidence":
                low_conf_total += 1
                if outcome["path_ok"]:
                    low_conf_ok_count += 1

        case_results.append(
            {
                "case_id": case["case_id"],
                "expect_path": outcome["expect_path"],
                "paths": outcome["paths"],
                "passed": outcome["passed"],
            }
        )

        if sleep_seconds and case_index < len(golden) - 1:
            time.sleep(sleep_seconds)

    return {
        "pass_count": pass_count,
        "total_cases": len(golden),
        "fallback_ok": fallback_ok_count,
        "fallback_total": fallback_total,
        "low_conf_ok": low_conf_ok_count,
        "low_conf_total": low_conf_total,
        "citations_invalid": citations_invalid_total,
        "cases": case_results,
    }


def format_summary(result: dict) -> str:
    return (
        f"eval pass={result['pass_count']}/{result['total_cases']} "
        f"fallback_ok={result['fallback_ok']}/{result['fallback_total']} "
        f"low_conf_ok={result['low_conf_ok']}/{result['low_conf_total']} "
        f"citations_invalid={result['citations_invalid']}"
    )


def format_case_line(case_result: dict) -> str:
    return (
        f"{case_result['case_id']} expect={case_result['expect_path']} "
        f"got={','.join(case_result['paths'])} passed={case_result['passed']}"
    )


def format_llm_stats_line(stats: Dict[str, int], last_model: Optional[str]) -> str:
    return (
        f"llm gemini={stats['gemini']} groq={stats.get('groq', 0)} "
        f"cache={stats['cache']} mock_fallback={stats['mock_fallback']} "
        f"model={last_model or '-'}"
    )


def format_report(
    result: dict, verbose: bool = False, llm_stats_line: Optional[str] = None
) -> str:
    lines = []
    if verbose:
        lines.extend(format_case_line(case_result) for case_result in result["cases"])
    if llm_stats_line is not None:
        lines.append(llm_stats_line)
    lines.append(format_summary(result))
    return "\n".join(lines)


def _parse_sleep(argv: List[str]) -> float:
    if "--sleep" not in argv:
        return 0.0
    idx = argv.index("--sleep")
    if idx + 1 >= len(argv):
        return 0.0
    try:
        return float(argv[idx + 1])
    except ValueError:
        return 0.0


def main(argv: Optional[List[str]] = None) -> dict:
    for _name in ("stdout", "stderr"):
        stream = getattr(sys, _name)
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    if argv is None:
        argv = sys.argv[1:]
    verbose = "--verbose" in argv
    llm_stats = "--llm-stats" in argv
    sleep_seconds = _parse_sleep(argv)

    if llm_stats:
        llm.reset_stats()

    result = run_golden_set(sleep_seconds=sleep_seconds)

    llm_stats_line = (
        format_llm_stats_line(llm.STATS, llm.LAST_MODEL) if llm_stats else None
    )
    print(format_report(result, verbose=verbose, llm_stats_line=llm_stats_line))
    return result


if __name__ == "__main__":
    main()
