from pathlib import Path
import shutil

CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".pptx", ".csv"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code": [".py", ".js", ".html", ".css", ".json"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Audio": [".mp3", ".wav", ".flac"],
}
DEFAULT_CATEGORY = "Others"


def get_category(filename):
    """Return the category folder name for a file, based on its extension."""
    extension = Path(filename).suffix.lower()
    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category
    return DEFAULT_CATEGORY


def unique_destination(destination):
    """If destination already exists, add _1, _2, ... so nothing is overwritten."""
    if not destination.exists():
        return destination
    counter = 1
    while True:
        candidate = destination.with_name(f"{destination.stem}_{counter}{destination.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def organise_files(folder, dry_run=False):
    """Sort the files in `folder` into category subfolders.

    Returns (moved, errors):
        moved  - list of (source, destination) paths
        errors - list of (source, error message)

    If dry_run is True, nothing is moved; `moved` shows what WOULD happen.
    Raises FileNotFoundError / NotADirectoryError for a bad folder path.
    """
    folder = Path(folder)
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")

    moved = []
    errors = []

    for item in folder.iterdir():
        if not item.is_file() or item.name.startswith("."):
            continue  # skip subfolders and hidden files

        target_dir = folder / get_category(item.name)
        destination = unique_destination(target_dir / item.name)

        if dry_run:
            moved.append((item, destination))
            continue

        try:
            target_dir.mkdir(exist_ok=True)
            shutil.move(str(item), str(destination))
            moved.append((item, destination))
        except (PermissionError, OSError) as error:
            errors.append((item, str(error)))

    return moved, errors


def print_report(moved, errors, dry_run=False):
    """Print a summary of what was (or would be) moved."""
    action = "Would move" if dry_run else "Moved"
    for source, destination in moved:
        print(f"{action}: {source.name} -> {destination.parent.name}/{destination.name}")
    for source, message in errors:
        print(f"FAILED: {source.name} ({message})")
    print(f"\n{len(moved)} file(s) {'to move' if dry_run else 'moved'}, {len(errors)} error(s).")


if __name__ == "__main__":
    try:
        path = input("Enter the folder to organise: ").strip().strip('"')
        moved, errors = organise_files(path, dry_run=True)
        if not moved:
            print("No files to organise.")
        else:
            print("\n--- Preview ---")
            print_report(moved, errors, dry_run=True)
            answer = input("\nProceed with moving these files? (y/n): ").strip().lower()
            if answer == "y":
                moved, errors = organise_files(path)
                print()
                print_report(moved, errors)
            else:
                print("Cancelled. No files were moved.")
    except (FileNotFoundError, NotADirectoryError) as error:
        print("Error:", error)
    except KeyboardInterrupt:
        print("\nCancelled.")
