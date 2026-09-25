import csv
from pathlib import Path

REQUIRED_FIELDS = ["name", "email"]
KEY_FIELD = "email"  # used to detect duplicate records


def read_records(path):
    """Read rows from a CSV file as a list of dicts.

    Raises FileNotFoundError if the file does not exist.
    """
    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        return list(reader), reader.fieldnames


def is_valid(record):
    """A record is valid if every required field has a value."""
    for field in REQUIRED_FIELDS:
        if not record.get(field, "").strip():
            return False
    return True


def process_records(records):
    """Split records into valid, invalid, and duplicate lists.

    Duplicates are found by comparing the KEY_FIELD (e.g. email).
    """
    valid = []
    invalid = []
    duplicates = []
    seen_keys = set()

    for record in records:
        if not is_valid(record):
            invalid.append(record)
            continue

        key = record.get(KEY_FIELD, "").strip().lower()
        if key in seen_keys:
            duplicates.append(record)
            continue

        seen_keys.add(key)
        valid.append(record)

    return valid, invalid, duplicates


def write_clean_file(records, fieldnames, output_path):
    """Write the valid, unique records to a new CSV file."""
    with open(output_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def print_report(total, valid, invalid, duplicates):
    print("=" * 50)
    print("DATA VALIDATION REPORT")
    print("=" * 50)
    print(f"Total records: {total}")
    print(f"Valid: {len(valid)}")
    print(f"Invalid (missing required fields): {len(invalid)}")
    for record in invalid:
        print(f"  {record}")
    print(f"Duplicates (same {KEY_FIELD}): {len(duplicates)}")
    for record in duplicates:
        print(f"  {record}")
    print("=" * 50)


if __name__ == "__main__":
    try:
        input_path = input("Enter CSV file to validate: ").strip().strip('"')
        records, fieldnames = read_records(input_path)

        if not records:
            print("The CSV file is empty.")
        else:
            valid, invalid, duplicates = process_records(records)
            print_report(len(records), valid, invalid, duplicates)

            output_path = "clean_records.csv"
            write_clean_file(valid, fieldnames, output_path)
            print(f"\nCleaned file written to: {output_path}")

    except FileNotFoundError:
        print("Error: file not found.")
    except KeyboardInterrupt:
        print("\nCancelled.")