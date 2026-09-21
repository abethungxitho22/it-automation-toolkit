import os
import tempfile
import time
import tracemalloc


def count_errors(path):
    """Count the lines containing ERROR in a log file."""
    count = 0
    with open(path, encoding="utf-8") as log_file:
        for line in log_file:
            if "ERROR" in line:
                count += 1
    return count


def make_big_log(path, line_count):
    """Write a large fake log file (every 10th line is an ERROR)."""
    with open(path, "w", encoding="utf-8") as log_file:
        for i in range(line_count):
            level = "ERROR" if i % 10 == 0 else "INFO"
            log_file.write(f"2026-09-21 08:00:00 {level} 10.0.0.{i % 250} Event number {i}\n")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "big.log")
        make_big_log(path, 300000)
        print(f"Log file size: {os.path.getsize(path) / 1024 / 1024:.1f} MB")

        tracemalloc.start()
        start = time.perf_counter()
        errors = count_errors(path)
        elapsed = time.perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    print("Errors found:", errors)
    print(f"Time taken: {elapsed:.2f} seconds")
    print(f"Peak memory used: {peak / 1024 / 1024:.1f} MB")
