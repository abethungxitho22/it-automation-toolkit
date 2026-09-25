import csv
import json
from datetime import datetime
from pathlib import Path


def build_summary(checks_performed, problems_detected, recommended_actions):
    """Combine the pieces of a report into one summary dict."""
    return {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "checks_performed": checks_performed,
        "problems_detected": problems_detected,
        "recommended_actions": recommended_actions,
    }


def write_text(summary, path):
    lines = [
        "=" * 50,
        "IT AUTOMATION TOOLKIT - SUMMARY REPORT",
        "=" * 50,
        f"Date: {summary['date']}",
        "",
        "Checks performed:",
    ]
    lines += [f"  - {item}" for item in summary["checks_performed"]] or ["  (none)"]
    lines += ["", "Problems detected:"]
    lines += [f"  - {item}" for item in summary["problems_detected"]] or ["  (none)"]
    lines += ["", "Recommended actions:"]
    lines += [f"  - {item}" for item in summary["recommended_actions"]] or ["  (none)"]
    lines.append("=" * 50)

    Path(path).write_text("\n".join(lines), encoding="utf-8")


def write_json(summary, path):
    Path(path).write_text(json.dumps(summary, indent=2), encoding="utf-8")


def write_csv(summary, path):
    with open(path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["date", summary["date"]])
        writer.writerow([])
        writer.writerow(["checks_performed"])
        for item in summary["checks_performed"]:
            writer.writerow([item])
        writer.writerow([])
        writer.writerow(["problems_detected"])
        for item in summary["problems_detected"]:
            writer.writerow([item])
        writer.writerow([])
        writer.writerow(["recommended_actions"])
        for item in summary["recommended_actions"]:
            writer.writerow([item])


def write_html(summary, path):
    def as_list(items):
        if not items:
            return "<li>(none)</li>"
        return "".join(f"<li>{item}</li>" for item in items)

    html = f"""<!DOCTYPE html>
<html>
<head><title>IT Automation Toolkit Report</title></head>
<body>
<h1>IT Automation Toolkit - Summary Report</h1>
<p><strong>Date:</strong> {summary['date']}</p>
<h2>Checks performed</h2>
<ul>{as_list(summary['checks_performed'])}</ul>
<h2>Problems detected</h2>
<ul>{as_list(summary['problems_detected'])}</ul>
<h2>Recommended actions</h2>
<ul>{as_list(summary['recommended_actions'])}</ul>
</body>
</html>"""
    Path(path).write_text(html, encoding="utf-8")


WRITERS = {
    "text": write_text,
    "json": write_json,
    "csv": write_csv,
    "html": write_html,
}


def generate_report(checks_performed, problems_detected, recommended_actions,
                     output_format="text", output_path=None):
    """Build and write a report. Returns the path written to."""
    if output_format not in WRITERS:
        raise ValueError(f"Unsupported format: {output_format}. Choose from {list(WRITERS)}")

    summary = build_summary(checks_performed, problems_detected, recommended_actions)

    if output_path is None:
        extension = "txt" if output_format == "text" else output_format
        output_path = f"reports/summary_report.{extension}"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    WRITERS[output_format](summary, output_path)
    return output_path


if __name__ == "__main__":
    # Example run using sample findings - replace with real results from
    # file_organiser.py, log_analyser.py, health_checker.py and data_validator.py
    checks_performed = [
        "File organisation (file_organiser.py)",
        "Log analysis (log_analyser.py)",
        "System health check (health_checker.py)",
        "Data validation (data_validator.py)",
    ]
    problems_detected = [
        "1 duplicate file found in test_data",
        "2 invalid records found in records.csv",
    ]
    recommended_actions = [
        "Review and remove confirmed duplicate files",
        "Correct or remove invalid records before re-import",
    ]

    fmt = input("Report format (text/json/csv/html) [text]: ").strip().lower() or "text"
    try:
        path = generate_report(checks_performed, problems_detected, recommended_actions,
                                output_format=fmt)
        print(f"Report written to: {path}")
    except ValueError as error:
        print("Error:", error)