# Troubleshooting Report — IT Operations Automation Toolkit (Capstone)

This report documents three real problems found and fixed while building and
testing the capstone toolkit, using the structured troubleshooting process
from Week 3:

1. Reproduce the problem
2. Identify the error or unexpected behaviour
3. Trace the problem to its root cause
4. Apply a fix
5. Run tests to confirm the fix
6. Document the solution to prevent it in future

---

## Issue 1: IndentationError and unreachable code in `file_organiser.py`

**1. Reproduce**
After adding duplicate-detection and invalid-filename-detection code to
`file_organiser.py`, the script failed to run at all.

**2. Identify**
Python raised an `IndentationError` pointing at the line defining
`VALID_NAME_PATTERN`. Separately, the call to `is_valid_name()` had been
placed inside the `if not item.is_file() or item.name.startswith("."):`
block, after its `continue` statement.

**3. Root cause**
- `VALID_NAME_PATTERN = re.compile(...)` had an extra leading space,
  putting it at the wrong indentation level for a module-level constant.
- The `is_valid_name()` check was nested inside a block that always exits
  early with `continue`, so that code could never execute even once the
  syntax error was fixed.

**4. Fix**
- Moved `VALID_NAME_PATTERN` to the constants section at the top of the
  file, correctly indented at module level.
- Moved the `is_valid_name()` check out of the `if ... continue` block so
  it runs for every file being processed, not just skipped ones.

**5. Confirm**
Re-ran the script against a test folder containing a file with a bad name
(`bad file!.txt`). The file was correctly flagged as invalid in the
console output and in `logs/file_organiser.log`, and the script no longer
crashed on startup.

**6. Prevention**
Watch indentation carefully when pasting code snippets into an existing
function — a single stray space can silently change which block a line
belongs to. Running the script immediately after each small change (rather
than after several changes at once) would have caught this sooner.

---

## Issue 2: UTF-8 BOM corrupting the first CSV column in `data_validator.py`

**1. Reproduce**
A CSV file was created on Windows using PowerShell's
`Out-File -Encoding utf8`. Running `data_validator.py` against this file
flagged **every** row as invalid, even rows with a name and email clearly
filled in.

**2. Identify**
Printing the invalid records showed the `name` field was actually stored
under the key `'\ufeffname'` — not `'name'`.

**3. Root cause**
PowerShell's `Out-File -Encoding utf8` writes a UTF-8 **Byte Order Mark
(BOM)** at the very start of the file. When Python opened the file with
`encoding="utf-8"`, the BOM character was not stripped, so it attached
itself to the first column header, turning `name` into `\ufeffname`. Since
`is_valid()` looked for the field `"name"` exactly, it never found it, and
every row failed the required-fields check.

**4. Fix**
Changed the file-opening encoding in `read_records()` from `"utf-8"` to
`"utf-8-sig"`, which automatically detects and strips a leading BOM if one
is present (and has no effect on files that don't have one).

**5. Confirm**
Re-ran the script against the same CSV file. All 6 records were read with
the correct column name (`name`, not `\ufeffname`), and the validation
report correctly identified 3 valid, 2 invalid, and 1 duplicate record.

**6. Prevention**
When a script's input files may come from Windows tools (Excel, PowerShell,
Notepad), always read CSV/text files with `utf-8-sig` rather than `utf-8`,
since these tools commonly add a BOM that plain `utf-8` does not handle.

---

## Issue 3: Duplicate-detection false positive in a unit test

**1. Reproduce**
After adding content-based duplicate detection to `file_organiser.py`
(hashing file contents instead of just comparing filenames), the existing
test `test_files_are_moved` started failing.

**2. Identify**
The test expected 3 files (`a.png`, `b.pdf`, `c.xyz`) to all be moved
successfully with no errors, but the function reported only 1 file moved
and 2 duplicate errors.

**3. Root cause**
The test's helper function `make_files()` wrote the exact same placeholder
text (`"test"`) into every sample file, regardless of file type. Once
duplicate detection compared file **content** (via an MD5 hash) rather than
filenames, all three files were correctly identified as duplicates of one
another — the test data was unrealistic, not the code.

**4. Fix**
Updated `test_files_are_moved` to write distinct content into each sample
file (`"image content"`, `"pdf content"`, `"mystery content"`), so the test
accurately reflects three genuinely different files.

**5. Confirm**
Re-ran the full test suite: `7/7 tests passed`.

**6. Prevention**
When a function's behaviour changes (here, duplicate detection moving from
name-based to content-based), review existing test fixtures for hidden
assumptions that no longer hold — in this case, that identical placeholder
content across files was harmless.

---

## Summary

| Issue | Area | Root cause | Fix |
|---|---|---|---|
| 1 | File automation | Indentation/scope error | Corrected placement of constant and validation check |
| 2 | Data validation | UTF-8 BOM from Windows tools | Read CSV with `utf-8-sig` instead of `utf-8` |
| 3 | Testing | Unrealistic test fixture data | Gave each test file distinct content |

All three issues were found through hands-on testing (manual runs and unit
tests) rather than by inspection alone, reinforcing the value of running
tests after every change rather than only at the end of development.