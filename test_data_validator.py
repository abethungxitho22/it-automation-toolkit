import tempfile
from pathlib import Path

from data_validator import (read_records, is_valid, process_records,
                            write_clean_file)


def expect_error(error_type, func, *args):
    try:
        func(*args)
    except error_type:
        return
    raise AssertionError(f"Should have raised {error_type.__name__}")


def test_is_valid_accepts_complete_record():
    assert is_valid({"name": "Alice", "email": "a@x.com"})


def test_is_valid_rejects_missing_or_blank_fields():
    assert not is_valid({"name": "", "email": "a@x.com"})
    assert not is_valid({"name": "Alice", "email": "   "})


def test_is_valid_handles_short_rows():
    # csv.DictReader gives None for columns missing from a short row
    assert not is_valid({"name": "Alice", "email": None})


def test_process_records_splits_valid_invalid_duplicate():
    records = [
        {"name": "Alice", "email": "alice@x.com"},
        {"name": "", "email": "bob@x.com"},
        {"name": "Alice", "email": "alice@x.com"},
        {"name": "Erin", "email": "erin@x.com"},
    ]
    valid, invalid, duplicates = process_records(records)
    assert len(valid) == 2
    assert len(invalid) == 1
    assert len(duplicates) == 1


def test_duplicates_ignore_case_and_spaces():
    records = [
        {"name": "Alice", "email": "alice@x.com"},
        {"name": "Alice B", "email": "  ALICE@x.com "},
    ]
    valid, _, duplicates = process_records(records)
    assert len(valid) == 1 and len(duplicates) == 1


def test_read_records_reads_csv():
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "r.csv"
        path.write_text("name,email\nAlice,a@x.com\n", encoding="utf-8")
        records, fieldnames = read_records(path)
        assert fieldnames == ["name", "email"]
        assert records == [{"name": "Alice", "email": "a@x.com"}]


def test_read_records_strips_windows_bom():
    # PowerShell's Out-File adds a BOM; it must not end up in the header
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "bom.csv"
        path.write_bytes(b"\xef\xbb\xbfname,email\nAlice,a@x.com\n")
        records, fieldnames = read_records(path)
        assert fieldnames[0] == "name"
        assert is_valid(records[0])


def test_missing_file_raises():
    expect_error(FileNotFoundError, read_records, "no/such/file.csv")


def test_write_clean_file_round_trip():
    with tempfile.TemporaryDirectory() as folder:
        out = Path(folder) / "clean.csv"
        rows = [{"name": "Alice", "email": "a@x.com"}]
        write_clean_file(rows, ["name", "email"], out)
        records, _ = read_records(out)
        assert records == rows


if __name__ == "__main__":
    tests = [f for name, f in list(globals().items()) if name.startswith("test_")]
    passed = 0
    for test in tests:
        try:
            test()
            print("PASS", test.__name__)
            passed += 1
        except Exception as error:
            print("FAIL", test.__name__, "-", type(error).__name__, error)
    print(f"\n{passed}/{len(tests)} tests passed")