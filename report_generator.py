import csv
import json
from datetime import datetime
from html import escape
from pathlib import Path


def build_summary(checks_performed, problems_detected, recommended_actions, metrics=None):
    """Combine the pieces of a report into one summary dict.

    `metrics` is optional and feeds the HTML dashboard's stat cards and chart:
        files_organised, log_errors, disk_percent, disk_threshold,
        records_valid, records_total, error_breakdown [[label, count], ...]
    """
    return {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "checks_performed": checks_performed,
        "problems_detected": problems_detected,
        "recommended_actions": recommended_actions,
        "metrics": metrics or {},
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


# ---------------------------------------------------------------- HTML dashboard
DASHBOARD_CSS = """
:root { --bg:#131313; --card:#1a1a1a; --line:#2b2b2b; --text:#f2f2f2; --muted:#9a9a9a;
        --red:#ef5350; --amber:#f5a623; --green:#3ecf5b; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--text); padding:32px 16px;
       font-family: Inter, "Segoe UI", Arial, sans-serif; }
.wrap { max-width:820px; margin:0 auto; }
.head { display:flex; justify-content:space-between; align-items:baseline;
        flex-wrap:wrap; gap:8px; margin-bottom:20px; }
h1 { font-size:20px; margin:0; font-weight:600; }
.stamp { color:var(--muted); font-size:14px; }
.stats { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:18px; }
.stat { border:1px solid var(--line); border-radius:12px; padding:16px 18px; background:var(--card); }
.stat .label { font-size:14px; }
.stat .value { font-size:30px; font-weight:500; margin-top:6px; }
.stat.red { background:#3a1010; border-color:#5a1c1c; }
.stat.red .label, .stat.red .value { color:#ff6b68; }
.stat.amber { background:#3a2308; border-color:#5a3a10; }
.stat.amber .label, .stat.amber .value { color:#f5a623; }
.stat.green { background:#0f2d12; border-color:#1b4a20; }
.stat.green .label, .stat.green .value { color:#3ecf5b; }
.card { border:1px solid var(--line); border-radius:12px; padding:18px 20px;
        background:var(--card); margin-bottom:16px; }
.card h2 { font-size:16px; margin:0 0 14px; display:flex; align-items:center; gap:8px; font-weight:600; }
.card svg { flex:none; }
.bar-row { display:grid; grid-template-columns:170px 1fr 30px; align-items:center;
           gap:12px; margin-bottom:10px; font-size:15px; }
.bar-row .name { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.track { background:#0e0e0e; border-radius:6px; height:8px; overflow:hidden; }
.fill { height:100%; border-radius:6px; }
.count { text-align:right; }
ul { margin:0; padding-left:20px; }
li { margin-bottom:8px; line-height:1.45; }
li.ok { list-style:none; margin-left:-20px; color:var(--green); }
@media (max-width:640px) {
  .stats { grid-template-columns:repeat(2,1fr); }
  .bar-row { grid-template-columns:110px 1fr 26px; }
}
"""

ICON_DOC = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/>'
            '<path d="M14 3v5h5M9 13h6M9 17h6"/></svg>')
ICON_CLIP = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
             'stroke-width="2"><path d="M9 4h6v3H9z"/><path d="M9 5.5H7a2 2 0 0 0-2 2V20a2 2 0 0 0 2 2h10'
             'a2 2 0 0 0 2-2V7.5a2 2 0 0 0-2-2h-2"/><path d="m9 14 2 2 4-4"/></svg>')
ICON_ALERT = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
              'stroke-width="2"><path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17'
              'a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/></svg>')
ICON_LIST = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
             'stroke-width="2"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>')


def _stat(label, value, tone=""):
    return (f'<div class="stat {tone}"><div class="label">{escape(label)}</div>'
            f'<div class="value">{escape(str(value))}</div></div>')


def _stat_cards(m):
    files = m.get("files_organised")
    errors = m.get("log_errors")
    disk = m.get("disk_percent")
    limit = m.get("disk_threshold", 90)
    valid, total = m.get("records_valid"), m.get("records_total")

    error_tone = "" if errors is None else ("red" if errors > 0 else "green")
    disk_tone = "" if disk is None else ("amber" if disk >= limit else "green")
    records_tone = "green" if total else ""
    return '<div class="stats">' + "".join([
        _stat("Files organized", "n/a" if files is None else files),
        _stat("Log errors found", "n/a" if errors is None else errors, error_tone),
        _stat("Disk usage", "n/a" if disk is None else f"{disk}%", disk_tone),
        _stat("Records cleaned", "n/a" if total is None else f"{valid}/{total}", records_tone),
    ]) + "</div>"


def _bars(rows):
    if not rows:
        return '<ul><li class="ok">No warnings or errors found</li></ul>'
    top = max(count for _, count in rows)
    out = []
    for i, (label, count) in enumerate(rows):
        width = max(6, round(count / top * 100))
        colour = "var(--red)" if i == 0 else "var(--amber)"
        out.append(f'<div class="bar-row"><span class="name" title="{escape(label)}">{escape(label)}</span>'
                   f'<div class="track"><div class="fill" style="width:{width}%;background:{colour}"></div></div>'
                   f'<span class="count">{count}</span></div>')
    return "".join(out)


def _list(items, empty_text):
    if not items:
        return f'<ul><li class="ok">{escape(empty_text)}</li></ul>'
    return "<ul>" + "".join(f"<li>{escape(item)}</li>" for item in items) + "</ul>"


def _card(icon, title, body):
    return f'<div class="card"><h2>{icon}{escape(title)}</h2>{body}</div>'


def write_html(summary, path):
    m = summary.get("metrics") or {}
    try:
        stamp = datetime.strptime(summary["date"], "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y, %H:%M")
    except ValueError:
        stamp = summary["date"]

    parts = [f'<div class="head"><h1>IT Operations Automation Toolkit</h1>'
             f'<span class="stamp">Report generated: {escape(stamp)}</span></div>']
    if m:
        parts.append(_stat_cards(m))
        parts.append(_card(ICON_DOC, "Log analysis", _bars(m.get("error_breakdown") or [])))
    parts.append(_card(ICON_LIST, "Checks performed", _list(summary["checks_performed"], "No checks run")))
    parts.append(_card(ICON_ALERT, "Problems detected", _list(summary["problems_detected"], "No problems detected")))
    parts.append(_card(ICON_CLIP, "Recommended actions", _list(summary["recommended_actions"], "No action needed")))

    page = ('<!DOCTYPE html><html><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>IT Automation Toolkit Report</title>'
            f'<style>{DASHBOARD_CSS}</style></head><body><div class="wrap">'
            + "".join(parts) + "</div></body></html>")
    Path(path).write_text(page, encoding="utf-8")


WRITERS = {
    "text": write_text,
    "json": write_json,
    "csv": write_csv,
    "html": write_html,
}


def generate_report(checks_performed, problems_detected, recommended_actions,
                     output_format="text", output_path=None, metrics=None):
    """Build and write a report. Returns the path written to."""
    if output_format not in WRITERS:
        raise ValueError(f"Unsupported format: {output_format}. Choose from {list(WRITERS)}")

    summary = build_summary(checks_performed, problems_detected, recommended_actions, metrics)

    if output_path is None:
        extension = "txt" if output_format == "text" else output_format
        output_path = f"reports/summary_report.{extension}"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    WRITERS[output_format](summary, output_path)
    return output_path


if __name__ == "__main__":
    # Example run using sample findings - main.py supplies the real results
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