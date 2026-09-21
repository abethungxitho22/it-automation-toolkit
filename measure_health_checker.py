"""Measure how long each health check takes.

Usage:
    python measure_health_checker.py
    python measure_health_checker.py --process chrome --runs 10
    python measure_health_checker.py --ping google.com
"""
import argparse
import time

from health_checker import check_disk, check_memory, check_ping, check_process
from pathlib import Path


def time_check(func, *args, runs=5):
    """Run func several times and return a list of durations in milliseconds."""
    durations = []
    for _ in range(runs):
        start = time.perf_counter()
        func(*args)
        durations.append((time.perf_counter() - start) * 1000)
    return durations


def main():
    parser = argparse.ArgumentParser(description="Time each health check.")
    parser.add_argument("--runs", type=int, default=5, help="repeats per check (default: 5)")
    parser.add_argument("--process", default="python", help="process name to look for")
    parser.add_argument("--ping", metavar="HOST", help="also time a ping to this host")
    args = parser.parse_args()

    checks = {
        "disk": (check_disk, Path.cwd().anchor, 90),
        "memory": (check_memory, 90),
        "process": (check_process, args.process),
    }
    if args.ping:
        checks["ping"] = (check_ping, args.ping)

    results = {}
    for name, (func, *func_args) in checks.items():
        print(f"Timing {name}...")
        results[name] = time_check(func, *func_args, runs=args.runs)

    total_avg = sum(sum(d) / len(d) for d in results.values())
    print()
    print(f"{'check':<10}{'runs':>5}{'min (ms)':>12}{'avg (ms)':>12}{'max (ms)':>12}{'share':>8}")
    print("-" * 59)
    for name, durations in sorted(results.items(), key=lambda item: -sum(item[1]) / len(item[1])):
        avg = sum(durations) / len(durations)
        share = avg / total_avg * 100
        print(f"{name:<10}{len(durations):>5}{min(durations):>12.2f}{avg:>12.2f}"
              f"{max(durations):>12.2f}{share:>7.0f}%")

    slowest = max(results, key=lambda name: sum(results[name]) / len(results[name]))
    print(f"\nSlowest check: {slowest}")


if __name__ == "__main__":
    main()
