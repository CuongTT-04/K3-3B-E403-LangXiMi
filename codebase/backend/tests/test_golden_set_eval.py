from eval.run_eval import format_case_line, format_report, format_summary, run_golden_set


def test_golden_set_runs_without_crashing_and_all_checks_hold():
    result = run_golden_set()

    assert result["total_cases"] >= 20
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


def test_verbose_report_prints_one_line_per_case_plus_summary():
    result = run_golden_set()

    report = format_report(result, verbose=True)
    lines = report.splitlines()

    assert len(lines) == result["total_cases"] + 1
    assert lines[-1] == format_summary(result)
    for case_result, line in zip(result["cases"], lines[:-1]):
        assert line == format_case_line(case_result)
        assert line.startswith(f"{case_result['case_id']} expect=")
        assert "got=" in line
        assert line.endswith(f"passed={case_result['passed']}")


def test_non_verbose_report_prints_only_the_summary_line():
    result = run_golden_set()

    report = format_report(result, verbose=False)

    assert report.splitlines() == [format_summary(result)]
