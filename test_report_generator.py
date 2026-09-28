import json
import tempfile
from pathlib import Path

from report_generator import build_summary, generate_report

CHECKS = ["File organisation", "Log analysis"]
PROBLEMS = ["2 invalid records found"]
ACTIONS = ["Correct invalid records"]


def expect_error(error_type, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except error_type:
        return
    raise AssertionError(f"Should have raised {error_type.__name__}")


def make_report(fmt, checks=CHECKS, problems=PROBLEMS, actions=ACTIONS):
    folder = tempfile.mkdtemp()
    path = Path(folder) / f"report.{fmt}"
    generate_report(checks, problems, actions, output_format=fmt, output_path=str(path))
    return path


def test_build_summary_has_required_parts():
    summary = build_summary(CHECKS, PROBLEMS, ACTIONS)
    assert summary["checks_performed"] == CHECKS
    assert summary["problems_detected"] == PROBLEMS
    assert summary["recommended_actions"] == ACTIONS
    assert summary["date"]


def test_text_report_contains_everything():
    text = make_report("text").read_text(encoding="utf-8")
    assert "Log analysis" in text
    assert "2 invalid records found" in text
    assert "Correct invalid records" in text


def test_json_report_is_valid_json():
    data = json.loads(make_report("json").read_text(encoding="utf-8"))
    assert data["problems_detected"] == PROBLEMS
    assert "date" in data


def test_csv_report_contains_sections():
    text = make_report("csv").read_text(encoding="utf-8")
    assert "checks_performed" in text
    assert "problems_detected" in text
    assert "recommended_actions" in text


def test_html_report_contains_everything():
    text = make_report("html").read_text(encoding="utf-8")
    assert "<html" in text.lower()
    assert "2 invalid records found" in text
    assert "Correct invalid records" in text


def test_empty_problems_are_handled():
    text = make_report("text", problems=[]).read_text(encoding="utf-8")
    assert "(none)" in text


def test_report_creates_missing_folder():
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "new_folder" / "report.json"
        generate_report(CHECKS, PROBLEMS, ACTIONS, output_format="json", output_path=str(path))
        assert path.exists()


def test_unsupported_format_raises():
    expect_error(ValueError, generate_report, CHECKS, PROBLEMS, ACTIONS, output_format="pdf")


def test_html_dashboard_shows_metrics():
    metrics = {"files_organised": 32, "log_errors": 14, "disk_percent": 91, "disk_threshold": 90,
               "records_valid": 118, "records_total": 121,
               "error_breakdown": [["Connection refused", 9], ["Timeout", 4]]}
    folder = tempfile.mkdtemp()
    path = Path(folder) / "r.html"
    generate_report(CHECKS, PROBLEMS, ACTIONS, output_format="html", output_path=str(path), metrics=metrics)
    text = path.read_text(encoding="utf-8")
    assert "Files organized" in text and ">32<" in text
    assert "91%" in text and "118/121" in text
    assert "Connection refused" in text


def test_html_without_metrics_still_works():
    text = make_report("html").read_text(encoding="utf-8")
    assert "Recommended actions" in text and "Files organized" not in text


def test_html_escapes_problem_text():
    text = make_report("html", problems=["<script>bad()</script>"]).read_text(encoding="utf-8")
    assert "<script>bad()" not in text and "&lt;script&gt;" in text


def test_summary_carries_metrics():
    summary = build_summary(CHECKS, PROBLEMS, ACTIONS, {"log_errors": 3})
    assert summary["metrics"] == {"log_errors": 3}


if __name__ == "__main__":
    tests = [f for name, f in list(globals().items()) if name.startswith("test_")]
    passed = 0
    for test in tests:
        try:
            test()
            print("PASS", test.__name__)
            passed += 1
        except Exception as error:
            print("FAIL", test.__name__, "-", type(error).__name__, error)
    print(f"\n{passed}/{len(tests)} tests passed")