import re
from collections import Counter

# Regular expressions (compiled once, reused for every line)
ERROR_PATTERN = re.compile(r"\b(ERROR|CRITICAL|FATAL)\b")
DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
IP_PATTERN = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
)


def read_log(path):
    """Read a log file and return its lines.

    Raises FileNotFoundError if the file does not exist.
    """
    with open(path, "r", encoding="utf-8", errors="replace") as log_file:
        return log_file.read().splitlines()


def extract_errors(lines):
    """Return the lines that contain ERROR, CRITICAL or FATAL."""
    return [line for line in lines if ERROR_PATTERN.search(line)]


def extract_dates(lines):
    """Return a Counter of dates (YYYY-MM-DD) and how often each appears."""
    dates = Counter()
    for line in lines:
        dates.update(DATE_PATTERN.findall(line))
    return dates


def extract_ips(lines):
    """Return a Counter of valid IPv4 addresses and how often each appears."""
    ips = Counter()
    for line in lines:
        ips.update(IP_PATTERN.findall(line))
    return ips


def build_report(lines):
    """Analyse the lines and return the report as a string."""
    errors = extract_errors(lines)
    dates = extract_dates(lines)
    ips = extract_ips(lines)

    report = ["=" * 50, "LOG ANALYSIS REPORT", "=" * 50]
    report.append(f"Total lines analysed: {len(lines)}")

    report.append(f"\nErrors found: {len(errors)}")
    for line in errors:
        report.append(f"  {line}")

    report.append("\nActivity by date:")
    for date, count in sorted(dates.items()):
        report.append(f"  {date}: {count} entries")

    report.append("\nIP addresses (most active first):")
    for ip, count in ips.most_common():
        report.append(f"  {ip}: {count} time(s)")

    report.append("=" * 50)
    return "\n".join(report)


if __name__ == "__main__":
    try:
        path = input("Enter log file path (press Enter for sample.log): ").strip().strip('"')
        if path == "":
            path = "sample.log"
        lines = read_log(path)
        if not lines:
            print("The log file is empty.")
        else:
            print(build_report(lines))
    except FileNotFoundError:
        print("Error: log file not found.")
    except PermissionError:
        print("Error: no permission to read that file.")
    except KeyboardInterrupt:
        print("\nCancelled.")
