import json
import tempfile
from pathlib import Path

from system_setup import (ConfigError, apply_plan, check_python_version, get_base_directory,
                          load_config, main, plan_actions, resolve_inside, validate_config)


def expect_error(error_type, func, *args):
    try:
        func(*args)
    except error_type:
        return
    raise AssertionError(f"Should have raised {error_type.__name__}")


SAMPLE = {
    "base_directory": "workspace",
    "required_python": "3.8",
    "folders": ["logs", "reports"],
    "files": [{"path": "config/settings.txt", "content": "level=INFO\n"}],
}


def write_config(folder, config):
    path = Path(folder) / "setup_config.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return str(path)


def statuses(actions):
    return [a.status for a in actions]


# ------------------------------------------------------ loading and validating
def test_load_config_missing_file():
    expect_error(ConfigError, load_config, "no_such_config.json")

def test_load_config_invalid_json():
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "bad.json"
        path.write_text("{ this is not json", encoding="utf-8")
        expect_error(ConfigError, load_config, path)

def test_load_config_valid():
    with tempfile.TemporaryDirectory() as folder:
        assert load_config(write_config(folder, SAMPLE))["base_directory"] == "workspace"

def test_validate_accepts_good_config():
    assert validate_config(dict(SAMPLE)) is not None

def test_validate_rejects_bad_configs():
    expect_error(ConfigError, validate_config, ["not", "an", "object"])
    expect_error(ConfigError, validate_config, {"folders": ["a"]})                        # no base_directory
    expect_error(ConfigError, validate_config, {"base_directory": "w", "folders": "logs"})  # not a list
    expect_error(ConfigError, validate_config, {"base_directory": "w", "files": [{"path": "a.txt"}]})  # no content
    expect_error(ConfigError, validate_config, {"base_directory": "w", "required_python": "three"})

def test_base_directory_is_relative_to_config_file():
    with tempfile.TemporaryDirectory() as folder:
        config_path = write_config(folder, SAMPLE)
        assert get_base_directory(SAMPLE, config_path) == (Path(folder) / "workspace").resolve()


# ------------------------------------------------------------------ safety
def test_resolve_inside_allows_normal_paths():
    with tempfile.TemporaryDirectory() as folder:
        assert resolve_inside(folder, "logs/app.log").name == "app.log"

def test_resolve_inside_blocks_escape_attempts():
    with tempfile.TemporaryDirectory() as folder:
        expect_error(ConfigError, resolve_inside, folder, "../outside.txt")
        outside = str(Path(folder).resolve().parent / "outside.txt")
        expect_error(ConfigError, resolve_inside, folder, outside)   # absolute path

def test_python_version_check():
    assert check_python_version("3.8", current=(3, 12))[0] is True
    assert check_python_version("3.12", current=(3, 12))[0] is True
    assert check_python_version("99.0", current=(3, 12))[0] is False
    assert check_python_version(None, current=(3, 12))[0] is True


# ------------------------------------------------------ planning and applying
def test_plan_on_empty_system_is_all_missing():
    with tempfile.TemporaryDirectory() as folder:
        base = Path(folder) / "workspace"
        assert set(statuses(plan_actions(SAMPLE, base))) == {"MISSING"}

def test_apply_creates_everything():
    with tempfile.TemporaryDirectory() as folder:
        base = Path(folder) / "workspace"
        results = apply_plan(plan_actions(SAMPLE, base))
        assert all(outcome == "CREATED" for _, outcome, _ in results)
        assert (base / "logs").is_dir() and (base / "reports").is_dir()
        assert (base / "config" / "settings.txt").read_text(encoding="utf-8") == "level=INFO\n"

def test_apply_is_idempotent():
    with tempfile.TemporaryDirectory() as folder:
        base = Path(folder) / "workspace"
        apply_plan(plan_actions(SAMPLE, base))
        second = apply_plan(plan_actions(SAMPLE, base))
        assert all(outcome == "UNCHANGED" for _, outcome, _ in second)

def test_drift_is_detected_and_not_overwritten_by_default():
    with tempfile.TemporaryDirectory() as folder:
        base = Path(folder) / "workspace"
        apply_plan(plan_actions(SAMPLE, base))
        settings = base / "config" / "settings.txt"
        settings.write_text("level=DEBUG\n", encoding="utf-8")          # someone edited it by hand
        assert "DIFFERENT" in statuses(plan_actions(SAMPLE, base))
        apply_plan(plan_actions(SAMPLE, base))                            # no --force
        assert settings.read_text(encoding="utf-8") == "level=DEBUG\n"     # left alone

def test_force_overwrites_drifted_file():
    with tempfile.TemporaryDirectory() as folder:
        base = Path(folder) / "workspace"
        apply_plan(plan_actions(SAMPLE, base))
        settings = base / "config" / "settings.txt"
        settings.write_text("level=DEBUG\n", encoding="utf-8")
        results = apply_plan(plan_actions(SAMPLE, base), force=True)
        assert settings.read_text(encoding="utf-8") == "level=INFO\n"
        assert "OVERWRITTEN" in [outcome for _, outcome, _ in results]

def test_conflict_when_file_blocks_a_folder():
    with tempfile.TemporaryDirectory() as folder:
        base = Path(folder) / "workspace"
        base.mkdir()
        (base / "logs").write_text("i am a file, not a folder", encoding="utf-8")
        actions = plan_actions(SAMPLE, base)
        assert "CONFLICT" in statuses(actions)
        results = apply_plan(actions, force=True)      # even --force must not delete it
        assert (base / "logs").is_file()
        assert "SKIPPED" in [outcome for _, outcome, _ in results]


# --------------------------------------------------------------- main()
def test_main_apply_then_dry_run_exit_codes():
    with tempfile.TemporaryDirectory() as folder:
        config_path = write_config(folder, SAMPLE)
        assert main(["--config", config_path, "--dry-run"]) == 1     # system does not match yet
        assert not (Path(folder) / "workspace").exists()              # dry run changed nothing
        assert main(["--config", config_path]) == 0                   # apply
        assert main(["--config", config_path, "--dry-run"]) == 0     # now it matches

def test_main_bad_config_returns_2():
    assert main(["--config", "no_such_config.json"]) == 2

def test_main_refuses_path_escape_and_creates_nothing_outside():
    with tempfile.TemporaryDirectory() as folder:
        evil = dict(SAMPLE, files=[{"path": "../escaped.txt", "content": "x"}])
        assert main(["--config", write_config(folder, evil)]) == 2
        assert not (Path(folder) / "escaped.txt").exists()

def test_main_old_python_stops_before_changing_anything():
    with tempfile.TemporaryDirectory() as folder:
        too_new = dict(SAMPLE, required_python="99.0")
        assert main(["--config", write_config(folder, too_new)]) == 1
        assert not (Path(folder) / "workspace").exists()


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
