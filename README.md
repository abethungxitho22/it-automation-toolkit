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

## Project structure

├── file_organiser.py
├── log_analyser.py
├── health_checker.py
├── test_file_organiser.py
├── test_log_analyser.py
├── test_health_checker.py
├── performance_lab/
├── system_setup.py
├── setup_config.json
├── test_system_setup.py
├── sample.log
├── .gitignore
└── README.md
```

## How this could help an IT department

- **File organiser:** tidy shared drives and download folders.
- **Log analyser:** spot repeated failed logins and suspicious IP addresses quickly.
- **Health checker:** run on a schedule to catch full disks, high memory use or stopped services before users notice.

## Week 3: Troubleshooting, Performance and Configuration Management

### Troubleshooting and debugging

During Week 3, deliberately broken Python scripts were investigated using a structured troubleshooting process:

1. Reproduce the problem.
2. Identify the error or unexpected behaviour.
3. Trace the problem to its root cause.
4. Apply a fix.
5. Run tests to confirm the fix.
6. Document the solution to help prevent the problem in future.

The troubleshooting work covered Python errors, logging, testing, exception handling and system reliability.

### Performance tuning

The performance lab was used to identify slow or resource-intensive operations.

The main improvements included:

* Optimising slow Python operations.
* Reducing unnecessary memory usage when processing large log files.
* Changing the log reader to process the file line by line instead of loading the entire file into memory.
* Adding log rotation so that log files do not grow indefinitely.

For the memory optimisation test, the log analyser still found **30,000 errors**, while peak memory usage decreased from approximately **48.4 MB to 0.1 MB**.

### Configuration management

The project includes a configuration-management script:

```text
system_setup.py
setup_config.json
test_system_setup.py
```

The setup script creates and maintains a standard workspace containing:

```text
toolkit_workspace/
├── logs/
├── reports/
├── backups/
├── config/
└── README.txt
```

The script is **idempotent**, meaning it can be run multiple times without unnecessarily changing an already correct configuration.

Configuration drift was also tested by deleting `README.txt`. Running the setup script again detected the missing file and recreated it while leaving the other configured items unchanged.

The configuration-management tests achieved:

```text
19/19 tests passed
```

### Cloud and virtual machine deployment

The automation toolkit can be moved from a local Windows computer to a Linux virtual machine or cloud server.

A possible deployment approach is:

```text
GitHub Repository
       |
       v
Linux Virtual Machine / Cloud Server
       |
       v
Python Environment
       |
       v
Automation Scripts
       |
       +--> File Organisation
       +--> Log Analysis
       +--> System Health Checks
       +--> Configuration Management
       |
       v
Logs and Reports
```

On a cloud or virtual machine, the scripts could be scheduled to run automatically using a scheduler such as `cron` on Linux or a cloud-based scheduling service.

The configuration file allows the environment to be recreated consistently, while log rotation helps prevent log files from growing indefinitely.

### Scalability and reliability

For a larger environment, the automation toolkit could be improved by:

* Running scripts on multiple virtual machines.
* Using scheduled jobs for regular health checks.
* Storing logs and reports centrally.
* Using cloud storage for backups.
* Adding monitoring and alerting.
* Using environment-specific configuration files.
* Running automated tests before deployment.

These improvements would make the automation solution easier to maintain and suitable for larger environments.
