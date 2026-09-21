import tempfile
from pathlib import Path

from file_organiser import get_category, organise_files, unique_destination


def expect_error(error_type, func, *args):
    try:
        func(*args)
    except error_type:
        return
    raise AssertionError(f"Should have raised {error_type.__name__}")


def make_files(folder, names):
    for name in names:
        (Path(folder) / name).write_text("test")


def test_get_category():
    assert get_category("photo.JPG") == "Images"
    assert get_category("report.pdf") == "Documents"
    assert get_category("backup.zip") == "Archives"
    assert get_category("mystery.xyz") == "Others"
    assert get_category("noextension") == "Others"

def test_files_are_moved():
    with tempfile.TemporaryDirectory() as folder:
        make_files(folder, ["a.png", "b.pdf", "c.xyz"])
        moved, errors = organise_files(folder)
        assert len(moved) == 3 and errors == []
        assert (Path(folder) / "Images" / "a.png").exists()
        assert (Path(folder) / "Documents" / "b.pdf").exists()
        assert (Path(folder) / "Others" / "c.xyz").exists()

def test_dry_run_moves_nothing():
    with tempfile.TemporaryDirectory() as folder:
        make_files(folder, ["a.png"])
        moved, _ = organise_files(folder, dry_run=True)
        assert len(moved) == 1
        assert (Path(folder) / "a.png").exists()
        assert not (Path(folder) / "Images").exists()

def test_no_overwrite_on_name_clash():
    with tempfile.TemporaryDirectory() as folder:
        (Path(folder) / "Images").mkdir()
        (Path(folder) / "Images" / "a.png").write_text("old")
        make_files(folder, ["a.png"])
        organise_files(folder)
        assert (Path(folder) / "Images" / "a.png").read_text() == "old"
        assert (Path(folder) / "Images" / "a_1.png").exists()

def test_subfolders_and_hidden_files_skipped():
    with tempfile.TemporaryDirectory() as folder:
        (Path(folder) / "SomeFolder").mkdir()
        make_files(folder, [".hidden.txt"])
        moved, _ = organise_files(folder)
        assert moved == []

def test_missing_folder():
    expect_error(FileNotFoundError, organise_files, "this/folder/does/not/exist")

def test_path_is_a_file_not_folder():
    with tempfile.TemporaryDirectory() as folder:
        make_files(folder, ["a.txt"])
        expect_error(NotADirectoryError, organise_files, str(Path(folder) / "a.txt"))


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
