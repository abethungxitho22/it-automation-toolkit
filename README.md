# IT Automation Toolkit

A collection of Python command-line tools that automate everyday IT tasks: organising files, analysing log files, and checking system health.

Built during the CAPACITI IT automation programme (Week 2: Operating-System Automation and GitHub).

## Tools

| Script | What it does |
|---|---|
| `file_organiser.py` | Sorts the files in a folder into category subfolders (Images, Documents, Archives, and more) |
| `log_analyser.py` | Extracts errors, dates and IP addresses from a log file and prints a summary report |
| `health_checker.py` | Checks disk usage, memory usage, network reachability and running processes |

Each script has a matching test file (`test_*.py`).

## Requirements

- Python 3.8 or newer
- No external packages needed. Everything uses the Python standard library.
- Tested on Windows. The health checker also runs on Linux.

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/abethungxitho22/it-automation-toolkit.git
   ```
2. Move into the folder:
   ```
   cd it-automation-toolkit
   ```
3. Check that Python is installed:
   ```
   python --version
   ```

## Usage

### File organiser

```
python file_organiser.py
```

Enter the path of the folder to organise. The script shows a **preview** of what it would move and asks for confirmation (`y/n`) before touching anything.

Example:

```
Would move: a.txt -> Documents/a.txt
Would move: b.png -> Images/b.png
Would move: c.zip -> Archives/c.zip

3 file(s) to move, 0 error(s).
Proceed with moving these files? (y/n):
```

Notes:
- Files are sorted by extension. Unknown types go into `Others`.
- Existing files are never overwritten. A clash is renamed (`a.png` becomes `a_1.png`).
- Subfolders and hidden files are skipped.
- Try it on a test folder with dummy files first.

### Log analyser

```
python log_analyser.py
```

Enter the path to a log file, or press Enter to analyse the included `sample.log`. The report shows:

- Lines containing `ERROR`, `CRITICAL` or `FATAL`
- Number of log entries per date (`YYYY-MM-DD`)
- Valid IPv4 addresses, ranked by how often they appear (invalid addresses such as `999.1.1.1` are ignored)

Expected log format:

```
2026-09-21 08:07:30 ERROR 10.0.0.5 Failed login for user admin
```

### System health checker

```
python health_checker.py
```

With no options it checks disk and memory usage. Add options for more checks:

| Option | Description |
|---|---|
| `--disk-path PATH` | Drive or folder to check (default: main drive) |
| `--disk-threshold N` | Fail if disk usage is above N% (default: 90) |
| `--memory-threshold N` | Fail if memory usage is above N% (default: 90) |
| `--ping HOST` | Also check that a host is reachable |
| `--process NAME` | Also check that a process is running |
| `-h`, `--help` | Show all options |

Examples:

```
python health_checker.py
python health_checker.py --ping google.com --process chrome
python health_checker.py --disk-threshold 80 --memory-threshold 70
```

Example output:

```
==================================================
SYSTEM HEALTH CHECK
==================================================
[OK]   Disk (C:\): 29.2% used, 336.9 GB free
[OK]   Memory: 45.0% used
[OK]   Ping: google.com is reachable
[OK]   Process: 'chrome' is running
==================================================
All checks passed.
```

Each check shows `[OK]`, `[FAIL]` or `[SKIP]` (skipped if it can't run on your system). The script exits with code `0` when everything passes and `1` when any check fails, so it can be used in scheduled tasks and other automation.

## Running the tests

Each script has its own test file. Run them from the project folder:

```
python test_file_organiser.py
python test_log_analyser.py
python test_health_checker.py
```

Every run should end with a line such as `14/14 tests passed`. The tests use temporary folders and mocked values, so they never touch your real files.

## Project structure

```
it-automation-toolkit/
├── file_organiser.py
├── log_analyser.py
├── health_checker.py
├── test_file_organiser.py
├── test_log_analyser.py
├── test_health_checker.py
├── sample.log
├── .gitignore
└── README.md
```

## How this could help an IT department

- **File organiser:** tidy shared drives and download folders.
- **Log analyser:** spot repeated failed logins and suspicious IP addresses quickly.
- **Health checker:** run on a schedule to catch full disks, high memory use or stopped services before users notice.
