"""Chạy đánh giá Golden Set (20 case) qua pipeline RAG + LLM + Validator.
In kết quả tổng hợp và lưu kết quả đo lường vào thư mục eval/run_results/.

Cách chạy:
    python eval/run_eval.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "src" / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Mặc định chạy MockLLM để đánh giá pipeline nhanh chóng (0.1s) và không tốn credit API.
# Nếu muốn chạy LLM thật (OpenRouter/Groq/Gemini), truyền flag: python eval/run_eval.py --real
if "--real" not in sys.argv:
    os.environ["LLM_MODE"] = "mock"

from app import data, service  


def _check_case(case: dict, quiz: dict, lessons_by_id: dict) -> dict:
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
            "case_id": case.get("case_id", "unknown"),
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
            "case_id": case.get("case_id", "unknown"),
            "passed": path_ok,
            "expect_path": expect_path,
            "path_ok": path_ok,
            "citations_invalid": citations_invalid,
        }

    # Happy path
    all_happy = all(item["path"] == "happy" for item in items)
    concepts_ok = any(item["concept"] in case["expected_concepts"] for item in items)
    cited_ids = {c["id"] for item in items for c in item["citations"]}
    expected_any = set(case.get("expected_source_ids_any", []))
    source_ok = not expected_any or bool(cited_ids & expected_any)
    case_passed = all_happy and concepts_ok and source_ok
    return {
        "case_id": case.get("case_id", "unknown"),
        "passed": case_passed,
        "expect_path": expect_path,
        "path_ok": case_passed,
        "citations_invalid": citations_invalid,
    }


def run_golden_set() -> dict:
    golden = data.load_golden_set()
    quiz = data.load_quiz("day01")
    lessons_by_id = data.index_lessons_by_id(data.load_lessons())

    details = []
    pass_count = 0
    fallback_total = 0
    fallback_ok_count = 0
    low_conf_total = 0
    low_conf_ok_count = 0
    citations_invalid_total = 0

    for case in golden:
        outcome = _check_case(case, quiz, lessons_by_id)
        details.append(outcome)
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

    pass_rate = round((pass_count / len(golden)) * 100, 1) if golden else 0.0

    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pass_count": pass_count,
        "total_cases": len(golden),
        "pass_rate_percent": pass_rate,
        "fallback_ok": fallback_ok_count,
        "fallback_total": fallback_total,
        "low_conf_ok": low_conf_ok_count,
        "low_conf_total": low_conf_total,
        "citations_invalid": citations_invalid_total,
        "quality_bar_passed": pass_rate >= 80.0 and citations_invalid_total == 0,
        "details": details,
    }


def main():
    result = run_golden_set()
    print("=" * 60)
    print("📊 KẾT QUẢ ĐÁNH GIÁ GOLDEN SET (QUALITY EVALUATION)")
    print("=" * 60)
    print(f"Tổng số case kiểm thử: {result['total_cases']}")
    print(f"Số case ĐẠT (PASS):    {result['pass_count']}/{result['total_cases']} ({result['pass_rate_percent']}%)")
    print(f"Fallback (No-grounding): {result['fallback_ok']}/{result['fallback_total']}")
    print(f"Low-confidence (G10):    {result['low_conf_ok']}/{result['low_conf_total']}")
    print(f"Trích dẫn ảo/sai:        {result['citations_invalid']} (Zero-tolerance)")
    status_str = "✓ ĐẠT QUALITY BAR (>= 80%)" if result['quality_bar_passed'] else "✗ CHƯA ĐẠT QUALITY BAR"
    print(f"Kết luận: {status_str}")
    print("=" * 60)

    # Lưu log vào eval/run_results/
    out_dir = ROOT_DIR / "eval" / "run_results"
    out_dir.mkdir(parents=True, exist_ok=True)
    log_file = out_dir / f"eval_run_{int(time.time())}.json"
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"💾 Đã lưu nhật ký đo lường vào: {log_file.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
