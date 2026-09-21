import random
import time


def find_high_readings(readings):
    """Return every reading that is within 1% of the highest reading."""
    highest = max(readings)
    alerts = []
    for reading in readings:
        if reading >= highest * 0.99:
            alerts.append(reading)
    return alerts


if __name__ == "__main__":
    random.seed(1)
    readings = [random.randint(1, 100000) for _ in range(4000)]
    print("Checking", len(readings), "readings...")

    start = time.perf_counter()
    alerts = find_high_readings(readings)
    elapsed = time.perf_counter() - start

    print("High readings found:", len(alerts))
    print(f"Time taken: {elapsed:.2f} seconds")
