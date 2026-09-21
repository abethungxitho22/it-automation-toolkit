import tempfile
import os

from log_analyser import read_log, extract_errors, extract_dates, extract_ips, build_report

SAMPLE = [
    "2026-09-21 08:01:12 INFO 192.168.1.10 User logged in",
    "2026-09-21 08:07:30 ERROR 10.0.0.5 Failed login",
    "2026-09-22 09:15:00 CRITICAL 172.16.0.8 Database lost",
    "2026-09-23 10:02:03 INFO 999.1.1.1 Invalid address",
    "2026-09-23 10:03:00 INFO 10.0.0.5 Another entry",
]


def expect_error(error_type, func, *args):
    try:
        func(*args)
    except error_type:
        return
    raise AssertionError(f"Should have raised {error_type.__name__}")


def test_extract_errors():
    errors = extract_errors(SAMPLE)
    assert len(errors) == 2
    assert all("ERROR" in e or "CRITICAL" in e for e in errors)

def test_extract_dates():
    dates = extract_dates(SAMPLE)
    assert dates["2026-09-21"] == 2
    assert dates["2026-09-23"] == 2

def test_extract_ips_counts():
    ips = extract_ips(SAMPLE)
    assert ips["10.0.0.5"] == 2
    assert ips["192.168.1.10"] == 1

def test_invalid_ip_ignored():
    ips = extract_ips(SAMPLE)
    assert "999.1.1.1" not in ips

def test_no_matches_returns_empty():
    assert extract_errors(["nothing to see here"]) == []
    assert len(extract_ips(["no addresses"])) == 0

def test_read_log_missing_file():
    expect_error(FileNotFoundError, read_log, "no_such_file.log")

def test_read_log_reads_lines():
    with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False) as f:
        f.write("line one\nline two\n")
        name = f.name
    try:
        assert read_log(name) == ["line one", "line two"]
    finally:
        os.remove(name)

def test_build_report_contains_sections():
    report = build_report(SAMPLE)
    assert "Errors found: 2" in report
    assert "10.0.0.5" in report


if __name__ == "__main__":
    tests = [f for name, f in list(globals().items()) if name.startswith("test_")]
    passed = 0
    for test in tests:
        try:
            test()
            print("PASS", test.__name__)
            passed += 1
        except AssertionError as error:
            print("FAIL", test.__name__, "-", error)
    print(f"\n{passed}/{len(tests)} tests passed")
