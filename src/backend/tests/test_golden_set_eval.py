from eval.run_eval import format_summary, run_golden_set


def test_golden_set_runs_without_crashing_and_all_checks_hold():
    result = run_golden_set()

    assert result["total_cases"] >= 10
    assert result["fallback_total"] >= 2
    assert result["low_conf_total"] >= 2
    assert result["citations_invalid"] == 0
    assert result["fallback_ok"] == result["fallback_total"]
    assert result["low_conf_ok"] == result["low_conf_total"]
    assert result["pass_count"] == result["total_cases"]


def test_format_summary_matches_expected_shape():
    line = format_summary(
        {
            "pass_count": 14,
            "total_cases": 14,
            "fallback_ok": 3,
            "fallback_total": 3,
            "low_conf_ok": 2,
            "low_conf_total": 2,
            "citations_invalid": 0,
        }
    )
    assert line == "eval pass=14/14 fallback_ok=3/3 low_conf_ok=2/2 citations_invalid=0"
