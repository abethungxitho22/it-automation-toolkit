import argparse
import ctypes
import logging
import platform
import shutil
import subprocess
import sys
from pathlib import Path

IS_WINDOWS = platform.system() == "Windows"

# ---------------------------------------------------------------- logging
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
# Next to the script (not the working directory), so it is always found
DEFAULT_LOG_FILE = Path(__file__).parent / "health_check.log"

logger = logging.getLogger("health_checker")
logger.addHandler(logging.NullHandler())  # stay quiet until logging is set up


def close_logging():
    """Close and remove any file handlers (used before re-configuring and in tests)."""
    for handler in list(logger.handlers):
        if isinstance(handler, logging.FileHandler):
            handler.close()
            logger.removeHandler(handler)


def setup_logging(log_file=DEFAULT_LOG_FILE, verbose=False):
    """Send log messages to a file. Returns True on success, False if the file can't be used.

    INFO and above are recorded normally; verbose=True adds DEBUG detail.
    """
    close_logging()  # avoids duplicate handlers (and duplicate lines) on repeat calls
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.propagate = False
    try:
        handler = logging.FileHandler(log_file, encoding="utf-8")
    except OSError as error:
        print(f"Warning: could not open log file {log_file} ({error}). Continuing without it.",
              file=sys.stderr)
        return False
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    return True


# ----------------------------------------------------------------- checks
def check_disk(path, threshold):
    """Check disk usage. Returns (status, message); status is True, False or None."""
    try:
        usage = shutil.disk_usage(path)
    except FileNotFoundError:
        logger.error("Disk path not found: %s", path)
        return False, f"Disk: path not found: {path}"
    except OSError as error:
        logger.error("Could not read disk %s: %s", path, error)
        return False, f"Disk: could not read {path} ({error})"

    percent_used = usage.used / usage.total * 100
    free_gb = usage.free / (1024 ** 3)
    logger.debug("Disk %s: total=%d used=%d free=%d bytes", path, usage.total, usage.used, usage.free)
    message = f"Disk ({path}): {percent_used:.1f}% used, {free_gb:.1f} GB free"
    return percent_used <= threshold, message


def get_memory_percent():
    """Return the percentage of memory in use, or None if it can't be read."""
    try:
        if IS_WINDOWS:
            class MemoryStatus(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            status = MemoryStatus()
            status.dwLength = ctypes.sizeof(MemoryStatus)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
            return float(status.dwMemoryLoad)

        # Linux: read /proc/meminfo
        values = {}
        with open("/proc/meminfo") as meminfo:
            for line in meminfo:
                key, number = line.split(":")[0], line.split(":")[1].split()[0]
                values[key] = int(number)
        return (1 - values["MemAvailable"] / values["MemTotal"]) * 100
    except (OSError, KeyError, ValueError, AttributeError):
        logger.error("Could not read memory usage", exc_info=True)
        return None


def check_memory(threshold):
    """Check memory usage. Returns (status, message)."""
    percent = get_memory_percent()
    if percent is None:
        return None, "Memory: could not be read on this system"
    return percent <= threshold, f"Memory: {percent:.1f}% used"


def run_command(command, timeout=10):
    """Run a command and return the finished process.

    Output is decoded as UTF-8 with errors="replace", so unreadable bytes
    (Windows tools like tasklist can print them) never crash the script.
    """
    logger.debug("Running command: %s", command)
    return subprocess.run(
        command,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def check_ping(host):
    """Ping a host once. Returns (status, message)."""
    flag = "-n" if IS_WINDOWS else "-c"
    try:
        result = run_command(["ping", flag, "1", host])
    except FileNotFoundError:
        logger.error("The ping command is not available on this system")
        return None, "Ping: the ping command is not available"
    except subprocess.TimeoutExpired:
        logger.error("Ping to %s timed out", host)
        return False, f"Ping: {host} timed out"

    logger.debug("Ping to %s returned exit code %s", host, result.returncode)
    if result.returncode == 0:
        return True, f"Ping: {host} is reachable"
    return False, f"Ping: {host} is NOT reachable"


def check_process(name):
    """Check whether a process with this name is running. Returns (status, message)."""
    command = ["tasklist"] if IS_WINDOWS else ["ps", "-e", "-o", "comm="]
    try:
        result = run_command(command)
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        logger.error("Could not list running processes: %s", error)
        return None, "Process: could not list running processes"

    output = result.stdout or ""
    if name.lower() in output.lower():
        return True, f"Process: '{name}' is running"
    return False, f"Process: '{name}' is NOT running"


# ------------------------------------------------------------ command line
def percentage(value):
    """argparse type: an integer between 1 and 100."""
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a whole number")
    if not 1 <= number <= 100:
        raise argparse.ArgumentTypeError("must be between 1 and 100")
    return number


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Command-line system health checker. Runs disk and memory "
                    "checks by default; add options for more."
    )
    parser.add_argument("--disk-path", default=Path.cwd().anchor,
                        help="drive or folder to check (default: main drive)")
    parser.add_argument("--disk-threshold", type=percentage, default=90,
                        help="warn if disk usage is above this %% (default: 90)")
    parser.add_argument("--memory-threshold", type=percentage, default=90,
                        help="warn if memory usage is above this %% (default: 90)")
    parser.add_argument("--ping", metavar="HOST",
                        help="also check that a host is reachable, e.g. google.com")
    parser.add_argument("--process", metavar="NAME",
                        help="also check that a process is running, e.g. chrome")
    parser.add_argument("--log-file", default=str(DEFAULT_LOG_FILE),
                        help="where to write the log (default: health_check.log next to the script)")
    parser.add_argument("--verbose", action="store_true",
                        help="record extra DEBUG detail in the log")
    return parser.parse_args(argv)


def run_checks(args):
    """Run the requested checks and return a list of (status, message)."""
    results = [
        check_disk(args.disk_path, args.disk_threshold),
        check_memory(args.memory_threshold),
    ]
    if args.ping:
        results.append(check_ping(args.ping))
    if args.process:
        results.append(check_process(args.process))
    return results


def main(argv=None):
    args = parse_args(argv)
    setup_logging(args.log_file, args.verbose)
    logger.info("Health check started (disk<=%s%%, memory<=%s%%)",
                args.disk_threshold, args.memory_threshold)

    print("=" * 50)
    print("SYSTEM HEALTH CHECK")
    print("=" * 50)

    results = run_checks(args)
    labels = {True: "[OK]  ", False: "[FAIL]", None: "[SKIP]"}
    for status, message in results:
        print(labels[status], message)
        if status is True:
            logger.info(message)
        else:
            logger.warning("%s: %s", "FAILED" if status is False else "SKIPPED", message)

    failures = sum(1 for status, _ in results if status is False)
    print("=" * 50)
    print("All checks passed." if failures == 0 else f"{failures} check(s) failed.")

    logger.info("Health check finished: %d check(s) failed", failures)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(1)
