"""Run the complete toolkit against isolated sample data, including setup drift checks."""

import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        shutil.copytree(root / "test_data", work / "test_data")
        for name in ("sample.log", "records.csv", "expected_files.txt", "setup_config.json"):
            shutil.copy2(root / name, work / name)
        subprocess.run(
            [sys.executable, str(root / "main.py"), "--format", "json"],
            cwd=work, check=True,
        )
        report = json.loads((work / "reports/summary_report.json").read_text(encoding="utf-8"))
        assert len(report["checks_performed"]) == 5, report
        assert report["date"] and report["recommended_actions"], report
        with (work / "clean_records.csv").open(encoding="utf-8", newline="") as handle:
            assert len(list(csv.DictReader(handle))) == 3
        assert (work / "logs/file_organiser.log").is_file()
        command = [sys.executable, str(root / "system_setup.py"), "--config", str(work / "setup_config.json")]
        subprocess.run(command, cwd=work, check=True)
        subprocess.run(command + ["--dry-run"], cwd=work, check=True)
    print("Smoke test passed: combined report, cleaned CSV, logs, and repeatable setup.")


if __name__ == "__main__":
    main()
