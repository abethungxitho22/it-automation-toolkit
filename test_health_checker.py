import argparse
import logging
import os
import sys
import tempfile
from contextlib import contextmanager
from unittest import mock

import health_checker
from health_checker import (check_disk, check_memory, check_ping, check_process,
                            parse_args, percentage, main, run_command,
                            setup_logging, close_logging)


def expect_error(error_type, func, *args):
    try:
        func(*args)
    except error_type:
        return
    raise AssertionError(f"Should have raised {error_type.__name__}")


@contextmanager
def temp_log_file():
    """Give a log path inside a temporary folder, and release the file afterwards."""
    with tempfile.TemporaryDirectory() as folder:
        try:
            yield os.path.join(folder, "test.log")
        finally:
            close_logging()  # Windows cannot delete a file that is still open


def quick_args(log_path, *extra):
    """Arguments for a fast, predictable run of main()."""
    return ["--disk-path", ".", "--disk-threshold", "100", "--memory-threshold", "100",
            "--log-file", log_path, *extra]


# ------------------------------------------------------------------ checks
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
    assert args.disk_threshold == 90 and args.ping is None and args.verbose is False
    args = parse_args(["--disk-threshold", "75", "--ping", "example.com", "--verbose"])
    assert args.disk_threshold == 75 and args.ping == "example.com" and args.verbose is True

def test_bad_argument_exits():
    expect_error(SystemExit, parse_args, ["--disk-threshold", "999"])

def test_main_exit_codes():
    with temp_log_file() as log_path:
        assert main(quick_args(log_path)) == 0
        assert main(["--disk-path", "no/such/place", "--log-file", log_path]) == 1


# ----------------------------------------------------------------- logging
def test_log_file_records_start_and_finish():
    with temp_log_file() as log_path:
        main(quick_args(log_path))
        close_logging()
        text = open(log_path, encoding="utf-8").read()
        assert "Health check started" in text
        assert "Health check finished: 0 check(s) failed" in text

def test_failed_check_is_logged_at_error_and_warning():
    with temp_log_file() as log_path:
        main(["--disk-path", "no/such/place", "--log-file", log_path])
        close_logging()
        text = open(log_path, encoding="utf-8").read()
        assert "ERROR" in text and "Disk path not found" in text   # the cause
        assert "WARNING" in text and "FAILED" in text              # the outcome

def test_debug_only_appears_with_verbose():
    with temp_log_file() as log_path:
        main(quick_args(log_path, "--process", "python"))
        close_logging()
        assert "DEBUG" not in open(log_path, encoding="utf-8").read()
        main(quick_args(log_path, "--process", "python", "--verbose"))
        close_logging()
        assert "DEBUG" in open(log_path, encoding="utf-8").read()

def test_setup_logging_does_not_duplicate_handlers():
    with temp_log_file() as log_path:
        setup_logging(log_path)
        setup_logging(log_path)
        file_handlers = [h for h in health_checker.logger.handlers
                         if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) == 1

def test_log_rotates_instead_of_growing_forever():
    with temp_log_file() as log_path:
        # Tiny limits so rotation happens quickly
        setup_logging(log_path, max_bytes=500, backup_count=2)
        for i in range(200):
            health_checker.logger.info("Filler message number %d to fill the log file", i)
        close_logging()

        folder = os.path.dirname(log_path)
        log_files = sorted(os.listdir(folder))
        assert "test.log.1" in log_files                       # rotation happened
        assert "test.log.3" not in log_files                   # only 2 backups kept
        assert len(log_files) <= 3                             # test.log + 2 backups
        for name in log_files:
            assert os.path.getsize(os.path.join(folder, name)) < 1000   # nothing huge

def test_unwritable_log_file_does_not_crash_the_script():
    # The folder does not exist, so the log file cannot be created
    result = main(quick_args("no_such_folder/health.log"))
    assert result == 0


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
