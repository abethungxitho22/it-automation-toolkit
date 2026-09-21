from unittest import mock

import health_checker
from health_checker import (check_disk, check_memory, check_ping, check_process,
                            parse_args, percentage, main, run_command)
import sys
import argparse


def expect_error(error_type, func, *args):
    try:
        func(*args)
    except error_type:
        return
    raise AssertionError(f"Should have raised {error_type.__name__}")


def test_disk_ok_with_high_threshold():
    status, message = check_disk(".", 100)
    assert status is True and "Disk" in message

def test_disk_threshold_logic_mocked():
    # Pretend the disk is 95% full: total=100, used=95, free=5 (in bytes)
    fake_usage = mock.Mock(total=100, used=95, free=5)
    with mock.patch("health_checker.shutil.disk_usage", return_value=fake_usage):
        assert check_disk(".", 90)[0] is False   # 95% > 90% -> fail
        assert check_disk(".", 95)[0] is True    # 95% <= 95% -> ok

def test_disk_bad_path():
    status, message = check_disk("no/such/place/anywhere", 90)
    assert status is False and "not found" in message

def test_memory_returns_status_and_message():
    status, message = check_memory(100)
    assert status in (True, None) and "Memory" in message

def test_process_finds_python():
    # This test is itself running inside a python process
    status, _ = check_process("python")
    assert status is True

def test_run_command_survives_undecodable_output():
    # Reproduces the Windows tasklist crash: output containing byte 0xff
    code = "import sys; sys.stdout.buffer.write(b'python \\xff end')"
    result = run_command([sys.executable, "-c", code])
    assert result.stdout is not None and "python" in result.stdout

def test_process_missing():
    status, _ = check_process("definitely_not_a_real_process_xyz")
    assert status is False

def test_ping_success_mocked():
    fake = mock.Mock(returncode=0)
    with mock.patch("health_checker.subprocess.run", return_value=fake):
        assert check_ping("example.com")[0] is True

def test_ping_failure_mocked():
    fake = mock.Mock(returncode=1)
    with mock.patch("health_checker.subprocess.run", return_value=fake):
        assert check_ping("example.com")[0] is False

def test_ping_command_missing_mocked():
    with mock.patch("health_checker.subprocess.run", side_effect=FileNotFoundError):
        assert check_ping("example.com")[0] is None

def test_percentage_validation():
    assert percentage("50") == 50
    expect_error(argparse.ArgumentTypeError, percentage, "abc")
    expect_error(argparse.ArgumentTypeError, percentage, "150")

def test_parse_args_defaults_and_options():
    args = parse_args([])
    assert args.disk_threshold == 90 and args.ping is None
    args = parse_args(["--disk-threshold", "75", "--ping", "example.com"])
    assert args.disk_threshold == 75 and args.ping == "example.com"

def test_bad_argument_exits():
    expect_error(SystemExit, parse_args, ["--disk-threshold", "999"])

def test_main_exit_codes():
    assert main(["--disk-path", ".", "--disk-threshold", "100", "--memory-threshold", "100"]) == 0
    assert main(["--disk-path", "no/such/place"]) == 1


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
