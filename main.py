"""
main.py - IT Operations Automation Toolkit

Runs all four automation modules in sequence against a target folder/files,
then generates a single combined summary report.

    python main.py
    python main.py --folder test_data --log sample.log --csv records.csv --format html
"""
import argparse
from pathlib import Path

from file_organiser import (organise_files, check_missing_files, read_expected_files,
                            print_report as print_file_report, write_log as write_file_log)
from log_analyser import read_log, extract_errors, extract_dates, extract_ips
from health_checker import check_disk, check_memory
from data_validator import read_records, process_records, write_clean_file
from report_generator import generate_report


def run_file_organiser(folder, expected_path=None):
    """Organise files in `folder` and check for missing files.
    Returns (checks, problems)."""
    checks = []
    problems = []
    try:
        moved, errors = organise_files(folder)
        print_file_report(moved, errors)
        checks.append(f"File organisation on '{folder}' ({len(moved)} moved)")

        if expected_path and Path(expected_path).exists():
            expected = read_expected_files(expected_path)
            missing = check_missing_files(folder, expected)
            for name in missing:
                print(f"MISSING: {name}")
                errors.append((Path(name), f"Missing file: expected '{name}' was not found"))
            checks.append(f"Missing-file check against '{expected_path}' "
                          f"({len(expected)} expected, {len(missing)} missing)")
        else:
            print(f"\nNo expected-files list found ({expected_path}) - skipping missing-file check")

        write_file_log(moved, errors)
        for _, message in errors:
            problems.append(f"File automation: {message}")
    except (FileNotFoundError, NotADirectoryError) as error:
        problems.append(f"File automation: {error}")
    return checks, problems


def run_log_analyser(log_path):
    """Analyse a log file. Returns (checks, problems)."""
    checks = []
    problems = []
    try:
        lines = read_log(log_path)
        errors = extract_errors(lines)
        dates = extract_dates(lines)
        ips = extract_ips(lines)
        print(f"\nLog analysis of '{log_path}': {len(lines)} lines, "
              f"{len(errors)} warning/error lines, {len(dates)} distinct dates, "
              f"{len(ips)} distinct IPs")
        checks.append(f"Log analysis on '{log_path}' ({len(lines)} lines)")
        if errors:
            problems.append(f"Log analysis: {len(errors)} warning/error line(s) found in {log_path}")
    except FileNotFoundError:
        problems.append(f"Log analysis: log file not found: {log_path}")
    return checks, problems


def run_health_checker(disk_path, disk_threshold=90, memory_threshold=90):
    """Run disk and memory checks. Returns (checks, problems)."""
    checks = ["System health check (disk, memory)"]
    problems = []

    disk_ok, disk_message = check_disk(disk_path, disk_threshold)
    print(f"\n{disk_message}")
    if disk_ok is False:
        problems.append(f"Health check: {disk_message}")

    memory_ok, memory_message = check_memory(memory_threshold)
    print(memory_message)
    if memory_ok is False:
        problems.append(f"Health check: {memory_message}")

    return checks, problems


def run_data_validator(csv_path):
    """Validate a CSV of records. Returns (checks, problems)."""
    checks = []
    problems = []
    try:
        records, fieldnames = read_records(csv_path)
        valid, invalid, duplicates = process_records(records)
        output_path = "clean_records.csv"
        write_clean_file(valid, fieldnames, output_path)
        print(f"\nData validation of '{csv_path}': {len(valid)} valid, "
              f"{len(invalid)} invalid, {len(duplicates)} duplicate(s)")
        checks.append(f"Data validation on '{csv_path}' ({len(valid)} valid records)")
        if invalid:
            problems.append(f"Data validation: {len(invalid)} record(s) missing required fields")
        if duplicates:
            problems.append(f"Data validation: {len(duplicates)} duplicate record(s) found")
    except FileNotFoundError:
        problems.append(f"Data validation: CSV file not found: {csv_path}")
    return checks, problems


def build_recommended_actions(problems):
    """Turn a list of problems into simple recommended actions."""
    if not problems:
        return ["No issues found - no action needed"]
    actions = []
    if any("duplicate" in p.lower() for p in problems):
        actions.append("Review and remove confirmed duplicate files/records")
    if any("missing file" in p.lower() for p in problems):
        actions.append("Locate or restore the missing files")
    if any("invalid" in p.lower() or "missing required" in p.lower() for p in problems):
        actions.append("Correct or remove invalid records and filenames")
    if any("warning" in p.lower() or "error" in p.lower() for p in problems):
        actions.append("Investigate warning/error lines flagged in the logs")
    if any("disk" in p.lower() or "memory" in p.lower() for p in problems):
        actions.append("Free up disk space or memory, or raise the alert threshold")
    if not actions:
        actions.append("Review the problems listed above")
    return actions


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="IT Operations Automation Toolkit - runs all checks and "
                    "produces one combined report."
    )
    parser.add_argument("--folder", default="test_data", help="folder to organise")
    parser.add_argument("--expected", default="expected_files.txt",
                        help="text file listing filenames that should exist (default: expected_files.txt)")
    parser.add_argument("--log", default="sample.log", help="log file to analyse")
    parser.add_argument("--disk-path", default=".", help="path to check disk usage on")
    parser.add_argument("--csv", default="records.csv", help="CSV file to validate")
    parser.add_argument("--format", default="text", choices=["text", "json", "csv", "html"],
                        help="report output format (default: text)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    print("=" * 60)
    print("IT OPERATIONS AUTOMATION TOOLKIT")
    print("=" * 60)

    all_checks = []
    all_problems = []

    for checks, problems in [
        run_file_organiser(args.folder, args.expected),
        run_log_analyser(args.log),
        run_health_checker(args.disk_path),
        run_data_validator(args.csv),
    ]:
        all_checks.extend(checks)
        all_problems.extend(problems)

    recommended_actions = build_recommended_actions(all_problems)

    report_path = generate_report(all_checks, all_problems, recommended_actions,
                                   output_format=args.format)

    print("\n" + "=" * 60)
    print(f"{len(all_checks)} check(s) run, {len(all_problems)} problem(s) found")
    print(f"Combined report written to: {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")