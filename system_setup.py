"""Configurable system setup script.

Reads the DESIRED state of a workspace from a JSON file (folders, files, minimum
Python version) and makes the machine match it.

    python system_setup.py                 create anything that is missing
    python system_setup.py --dry-run       show what would change, change nothing
    python system_setup.py --force         also overwrite files whose content differs
    python system_setup.py --config my.json

Running it twice is safe: the second run finds nothing to do (idempotent).
"""
import argparse
import json
import re
import sys
from collections import namedtuple
from pathlib import Path

# Next to the script, not the working directory, so it works from any folder
DEFAULT_CONFIG = Path(__file__).parent / "setup_config.json"

Action = namedtuple("Action", "kind relative path status content detail")


class ConfigError(ValueError):
    """The configuration file is missing, unreadable or invalid."""


# ------------------------------------------------------------ configuration
def load_config(path):
    """Read a JSON config file. Raises ConfigError with a clear message on failure."""
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}")
    except OSError as error:
        raise ConfigError(f"Could not read config file {path}: {error}")
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise ConfigError(f"Config file is not valid JSON: {error}")


def validate_config(config):
    """Check the config has the right shape. Returns it, or raises ConfigError."""
    if not isinstance(config, dict):
        raise ConfigError("Config must be a JSON object")

    base = config.get("base_directory")
    if not isinstance(base, str) or not base.strip():
        raise ConfigError("'base_directory' is required and must be non-empty text")

    folders = config.get("folders", [])
    if not isinstance(folders, list) or not all(isinstance(f, str) and f.strip() for f in folders):
        raise ConfigError("'folders' must be a list of folder names")

    files = config.get("files", [])
    if not isinstance(files, list):
        raise ConfigError("'files' must be a list")
    for entry in files:
        if not isinstance(entry, dict):
            raise ConfigError("each item in 'files' must be an object with 'path' and 'content'")
        if not isinstance(entry.get("path"), str) or not entry["path"].strip():
            raise ConfigError("each file needs a non-empty 'path'")
        if not isinstance(entry.get("content"), str):
            raise ConfigError(f"file '{entry['path']}' needs 'content' as text")

    required = config.get("required_python")
    if required is not None and (not isinstance(required, str) or not re.fullmatch(r"\d+\.\d+", required)):
        raise ConfigError("'required_python' must look like \"3.8\"")

    return config


def get_base_directory(config, config_path):
    """The base directory is relative to the CONFIG FILE, not the working directory."""
    return (Path(config_path).parent / config["base_directory"]).resolve()


def resolve_inside(base, relative):
    """Return base/relative, refusing any path that escapes the base directory."""
    base = Path(base).resolve()
    target = (base / relative).resolve()
    if target != base and base not in target.parents:
        raise ConfigError(f"Path is outside the base directory: {relative}")
    return target


def check_python_version(required, current=None):
    """Return (ok, message) comparing the running Python with the required version."""
    current = current or sys.version_info[:2]
    if required is None:
        return True, f"Python {current[0]}.{current[1]}"
    needed = tuple(int(part) for part in required.split("."))
    if tuple(current) >= needed:
        return True, f"Python {current[0]}.{current[1]} (needs {required} or newer)"
    return False, f"Python {current[0]}.{current[1]} is too old (needs {required} or newer)"


# --------------------------------------------------------- plan and apply
def plan_actions(config, base_dir):
    """Compare the desired state with the real system. Changes nothing.

    Each action has a status:
        OK        already matches the config
        MISSING   does not exist yet
        DIFFERENT exists, but the file content differs from the config
        CONFLICT  something of the wrong type is in the way
    """
    actions = []

    for relative in config.get("folders", []):
        path = resolve_inside(base_dir, relative)
        if not path.exists():
            status, detail = "MISSING", ""
        elif path.is_dir():
            status, detail = "OK", "exists"
        else:
            status, detail = "CONFLICT", "a file exists where a folder is needed"
        actions.append(Action("folder", relative, path, status, None, detail))

    for entry in config.get("files", []):
        relative, content = entry["path"], entry["content"]
        path = resolve_inside(base_dir, relative)
        if not path.exists():
            status, detail = "MISSING", ""
        elif path.is_dir():
            status, detail = "CONFLICT", "a folder exists where a file is needed"
        else:
            try:
                same = path.read_text(encoding="utf-8") == content
                status, detail = ("OK", "content matches") if same else ("DIFFERENT", "content differs")
            except UnicodeDecodeError:
                status, detail = "DIFFERENT", "content differs (not readable as text)"
            except OSError as error:
                status, detail = "CONFLICT", f"could not read it ({error})"
        actions.append(Action("file", relative, path, status, content, detail))

    return actions


def apply_plan(actions, force=False):
    """Carry out the plan. Returns a list of (action, outcome, message).

    Outcomes: UNCHANGED, CREATED, OVERWRITTEN, SKIPPED, FAILED.
    """
    results = []
    for action in actions:
        if action.status == "OK":
            results.append((action, "UNCHANGED", action.detail))
        elif action.status == "CONFLICT":
            results.append((action, "SKIPPED", action.detail))
        elif action.status == "DIFFERENT" and not force:
            results.append((action, "SKIPPED", "content differs (use --force to overwrite)"))
        else:
            try:
                if action.kind == "folder":
                    action.path.mkdir(parents=True, exist_ok=True)
                else:
                    action.path.parent.mkdir(parents=True, exist_ok=True)
                    action.path.write_text(action.content, encoding="utf-8")
                outcome = "OVERWRITTEN" if action.status == "DIFFERENT" else "CREATED"
                results.append((action, outcome, ""))
            except OSError as error:
                results.append((action, "FAILED", str(error)))
    return results


# ------------------------------------------------------------ command line
def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Create a workspace from a JSON configuration file. "
                    "Safe to run repeatedly."
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG),
                        help="path to the JSON config (default: setup_config.json next to the script)")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would change without changing anything "
                             "(exit code 1 if the system does not match the config)")
    parser.add_argument("--force", action="store_true",
                        help="overwrite files whose content differs from the config")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    print("=" * 60)
    print("SYSTEM SETUP" + (" (dry run)" if args.dry_run else ""))
    print("=" * 60)

    try:
        config = validate_config(load_config(args.config))
        base_dir = get_base_directory(config, args.config)
        actions = plan_actions(config, base_dir)
    except ConfigError as error:
        print("Configuration error:", error)
        return 2

    print("Config:", args.config)
    print("Base directory:", base_dir)
    print()

    python_ok, python_message = check_python_version(config.get("required_python"))
    print(("[OK]        " if python_ok else "[FAIL]      ") + python_message)
    if not python_ok:
        print("\nNothing was changed. Fix the environment first.")
        return 1

    if args.dry_run:
        for action in actions:
            note = f" ({action.detail})" if action.detail else ""
            print(f"[{action.status:<9}] {action.kind} {action.relative}{note}")
        needs_change = [a for a in actions if a.status != "OK"]
        print("=" * 60)
        if needs_change:
            print(f"{len(needs_change)} item(s) do not match the config. Nothing was changed.")
            return 1
        print("Everything already matches the config.")
        return 0

    results = apply_plan(actions, force=args.force)
    for action, outcome, message in results:
        note = f" ({message})" if message else ""
        print(f"[{outcome:<11}] {action.kind} {action.relative}{note}")

    counts = {}
    for _, outcome, _ in results:
        counts[outcome] = counts.get(outcome, 0) + 1
    print("=" * 60)
    if all(outcome == "UNCHANGED" for _, outcome, _ in results):
        print("Nothing to do. Everything already matches the config.")
    else:
        print("Summary:", ", ".join(f"{count} {name.lower()}" for name, count in counts.items()))

    problems = counts.get("SKIPPED", 0) + counts.get("FAILED", 0)
    return 0 if problems == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(1)
