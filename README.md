# IT Automation Toolkit

A collection of Python command-line tools that automate everyday IT tasks: organising files, analysing log files, checking system health, validating data, and generating reports.

Built during the CAPACITI IT automation programme (Week 2: Operating-System Automation and GitHub; Week 4: Real-World Automation and Capstone Project).

## Tools

| Script | What it does |
|---|---|
| `file_organiser.py` | Sorts the files in a folder into category subfolders (Images, Documents, Archives, and more), flags duplicate, badly named and missing files, and logs every change |
| `log_analyser.py` | Extracts errors, dates and IP addresses from a log file and prints a summary report |
| `health_checker.py` | Checks disk usage, memory usage, network reachability and running processes |
| `data_validator.py` | Reads records from a CSV, validates required fields, flags duplicates, and writes a cleaned output file |
| `report_generator.py` | Generates a summary report (checks performed, problems found, recommended actions) in text, JSON, CSV or HTML format |
| `main.py` | Runs all four modules together in one command and produces a single combined report |

Each script has a matching test file (`test_*.py`).

## Requirements

- Python 3.8 or newer
- No external runtime packages needed. Everything uses the Python standard library.
- CI/development tools require Python 3.12 or newer and `requirements-dev.txt`.
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
- Files are also checked for duplicate content (by hash) and invalid characters in the filename; both are flagged and logged.
- **Missing files:** after moving, you can give the script a list of expected filenames (one per line, like `expected_files.txt`). Any name that can't be found in the folder or its category subfolders is reported as `MISSING` and written to the log. Blank lines and lines starting with `#` in the list are ignored.
- Try it on a test folder with dummy files first.

### Log analyser

```
python log_analyser.py
```

Enter the path to a log file, or press Enter to analyse the included `sample.log`. The report shows:

- Lines containing `ERROR`, `CRITICAL`, `FATAL` or `WARNING`
- Repeated errors (the same line occurring more than once)
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

### Data validator

```
python data_validator.py
```

Enter the path to a CSV file. Records missing required fields (`name`, `email`) are flagged as invalid; records with a repeated email are flagged as duplicates. A cleaned CSV of valid, unique records is written to `clean_records.csv`.

### Report generator

```
python report_generator.py
```

Choose an output format (`text`, `json`, `csv`, `html`). Produces `reports/summary_report.<format>` containing the date, checks performed, problems detected, and recommended actions.

### Running everything at once

```
python main.py --folder test_data --log sample.log --csv records.csv --format html
```

Runs the file organiser (including the missing-file check), log analyser, health checker and data validator in sequence, then writes one combined report covering all of them.

| Option | Description | Default |
|---|---|---|
| `--folder` | Folder to organise | `test_data` |
| `--expected` | Text file listing filenames that should exist | `expected_files.txt` |
| `--log` | Log file to analyse | `sample.log` |
| `--disk-path` | Path to check disk usage on | `.` |
| `--csv` | CSV file to validate | `records.csv` |
| `--format` | Report format: `text`, `json`, `csv`, `html` | `text` |

If the expected-files list isn't found, the missing-file check is skipped and the rest of the toolkit still runs.

## Running the tests

Run the full suite with the same failure handling used by GitHub Actions:

```sh
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m pytest -q
python scripts/smoke_test.py
```

The smoke test runs the combined toolkit on temporary copies of the sample data,
checks the JSON report, cleaned CSV and log, and verifies that system setup is
repeatable. The workflow tests Python 3.12 and 3.14 on Windows and Linux.

Each script has its own test file. Run them from the project folder:

```
python test_file_organiser.py
python test_log_analyser.py
python test_health_checker.py
python test_data_validator.py
python test_report_generator.py
python test_system_setup.py
```

Every standalone run should end with a line such as `14/14 tests passed`. Those
standalone runners can print failures and still exit successfully; use pytest
for an enforceable pass/fail result. Tests use temporary folders and mocked values.

## GitHub Actions CI/CD

The workflow is [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml).
It runs on branch/tag pushes, pull requests, and **Actions → Toolkit CI/CD → Run
workflow**. A branch push with an open pull request can produce two runs.

```text
Lint → Tests → Build + container smoke test → Image scan → Publish → Deploy
```

| Stage | Required result |
|---|---|
| Lint | Ruff passes across the Python source, tests and labs |
| Tests | All four OS/Python combinations pass pytest and the integrated smoke test |
| Build | Docker image builds and passes its own smoke test as a non-root user |
| Image scan | Trivy finds no HIGH/CRITICAL vulnerabilities or secrets; scanner errors also fail the job |
| Publish | `develop` and default branch: upload the exact scanned image to GitHub Container Registry (GHCR) |
| Deploy | Separate manual workflow: rescan a selected digest, then execute it on the Linux deployment runner |

Every automatic stage depends on the previous stage passing. Deployment is a separate manual workflow in `.github/workflows/deploy.yml`. Images are built once and
passed between jobs as an artifact; publishing does not rebuild them. Vulnerabilities
without a fix also block release. Review `image-scan/trivy.json` in the run's
artifacts, update affected components, and rerun the pipeline. Findings are also
printed in the scan job log, with affected packages, installed
versions and fixed versions; counts appear in the job summary. Secret match
contents are omitted from the printed summary. Treat the full JSON artifact as
sensitive if secrets are detected. An exit code of 1 after scanning means the
gate failed, not that Docker failed to download the scanner image. The scanner image
is pinned by digest. Test/scan artifacts last 14 days; the image archive lasts
3 days. Rerun the complete workflow if the image artifact has expired.

### Enable CI and image publishing

1. Commit and push these files to GitHub. No GitLab configuration is needed.
2. Ensure GitHub Actions is enabled and repository/organisation policy permits
   the official checkout, Python setup and artifact actions used by the workflow.
3. Push to `develop` or the repository's default branch to publish to
   `ghcr.io/<owner>/it-automation-toolkit`. Publishing uses the built-in
   `GITHUB_TOKEN` with `packages: write`; no registry password secret is needed.
   If a GHCR package already exists, grant this repository Actions access to it.
4. Use the digest printed in the publish job summary for deployments or rollback.
   Each run gets a unique `sha-<commit>-<run-id>-<attempt>` image tag.

Pull requests and branches other than `develop` or the default branch validate and scan without publishing. Tags do not publish. Pushes never deploy. Fork pull requests use GitHub-hosted runners and receive no deployment
credentials. For branch protection, require **Lint**, all four **Test** checks,
**Build and smoke-test image**, and **Scan image**; do not require the conditional
publish/deploy jobs.

### Configure deployment to a Linux Docker host

The toolkit is a one-shot batch application: deployment runs it to completion
and stores outputs on the host. It does not start a web server. Host deployment
runs only when manually requested; CI and GHCR publishing work independently.

1. Register a dedicated Linux x64 self-hosted Actions runner on the target server
   with the custom label `toolkit-deploy`. Install Docker and Bash and allow the
   runner account to run Docker. Keep this runner restricted to trusted workflows.
2. Create the GitHub environment **production**, allowing deployment branches
   `develop` and the default branch. Configure required reviewers if your team needs them.
3. Prepare a dedicated writable workspace, owned by the runner account:

   ```text
   /srv/it-automation-toolkit/
   ├── inbox/              # Files the organiser is allowed to MOVE
   ├── application.log     # Input log
   ├── records.csv         # Input CSV
   └── expected_files.txt  # Expected filenames, one per line
   ```

4. Under **Settings → Secrets and variables → Actions → Variables**, set these
   repository variables:

   | Variable | Value |
   |---|---|
   | `DEPLOY_ENABLED` | `true` to enable the deployment job |
   | `TOOLKIT_DATA_DIR` | Absolute host path, for example `/srv/it-automation-toolkit` |

5. Merge `.github/workflows/deploy.yml` into the default branch once so GitHub
   displays its manual trigger. Then open **Actions ? Deploy toolkit manually ?
   Run workflow**, choose `develop` or the default branch, and paste the full
   `ghcr.io/<owner>/<repository>@sha256:<digest>` from a successful publish summary.
   The workflow validates the configuration and rescans that exact image before
   deployment. It runs with the runner's UID/GID so mounted data remains writable.
   Setting `DEPLOY_ENABLED=true` enables manual deployment; it never deploys on push.
   See [GitHub manual workflow requirements](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

Use copies of the sample inputs for the first deployment. The organiser moves
files inside `inbox`; each run overwrites `clean_records.csv` and
`reports/summary_report.json`, and appends `logs/file_organiser.log`. Back up
important inputs and manage log retention on the host. Deployment jobs are
serialized. No scheduled processing is configured.

The job verifies that all five checks completed and the cleaned CSV exists.
Reported operational problems (such as duplicate records or high memory use)
are report findings, not deployment failures: `main.py` records these and can
exit zero. Container health information reflects the container's view of the
system; it is not a complete host-monitoring solution.

To rerun a previous release on the host, use its digest with the same mount and
arguments shown in the deploy job. This rolls back the code only; it does not
undo file moves or restore overwritten output files.

### Build and verify the container locally

With a running Docker engine in Linux-container mode:

```sh
docker build --pull -t toolkit:local .
docker run --rm toolkit:local --help
```

On Linux/macOS (or Git Bash with Docker path conversion configured), run the
isolated smoke test inside the image:

```sh
docker run --rm --entrypoint python \
  --mount "type=bind,src=$PWD/scripts/smoke_test.py,dst=/tmp/smoke_test.py,readonly" \
  toolkit:local /tmp/smoke_test.py /app
```

The image includes runtime modules and sample fixtures, and defaults to `--help`
to avoid moving files accidentally. Tests, development dependencies, Git history
and existing output reports are excluded from the build context.

The runtime uses the official `python:3.12-alpine3.24` image, applies available
Alpine package updates, and installs `procps` and `iputils` for process and ping
checks. This replaces the Debian 12 base after its scan reported HIGH/CRITICAL
OS-package findings without listed fixes. The vulnerability gate remains strict;
changing the base is not a guarantee of a clean scan. The container smoke checks
also verify process discovery and the presence of the ping executable.
After a Dockerfile change, push a new commit or start a new full workflow run;
rerunning only the failed scan reuses the old image artifact.

This CI/CD extension supports the curriculum's Week 3 deployment/reliability and
Week 4 integration, testing and demonstration work. The curriculum is project
context; it does not itself require GitHub Actions or container scanning.
References: [GitHub image publishing](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images),
[GHCR access](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry),
and [Trivy image scanning](https://trivy.dev/docs/dev/references/configuration/cli/trivy_image/).

## Project structure

CI/CD files: `.github/workflows/ci-cd.yml`, `.github/actionlint.yaml`, `Dockerfile`,
`.dockerignore`, `requirements-dev.txt`, `pyproject.toml`, and `scripts/smoke_test.py`.

```
├── file_organiser.py
├── log_analyser.py
├── health_checker.py
├── data_validator.py
├── report_generator.py
├── main.py
├── test_file_organiser.py
├── test_log_analyser.py
├── test_health_checker.py
├── test_data_validator.py
├── test_report_generator.py
├── performance_lab/
├── system_setup.py
├── setup_config.json
├── test_system_setup.py
├── sample.log
├── records.csv
├── clean_records.csv
├── expected_files.txt
├── test_data/
├── logs/
├── reports/
├── troubleshooting_report.md
├── .gitignore
└── README.md
```

## Sample input and output files

Inputs:

- `test_data/`: sample files to organise (mixed types, a duplicate, a badly named file)
- `expected_files.txt`: filenames that should exist (includes `budget.xlsx`, which is deliberately absent so the missing-file check has something to find)
- `sample.log`: log file for the log analyser
- `records.csv`: user records for the data validator (includes invalid and duplicate rows)

Outputs:

- `clean_records.csv`: valid, unique records written by the data validator
- `logs/file_organiser.log`: every file moved and every problem found by the file organiser
- `reports/summary_report.html` (also `.txt`, `.json`, `.csv`): the combined report from `main.py`

## Troubleshooting

Problems found and fixed while building the capstone toolkit are documented in `troubleshooting_report.md`.

## How this could help an IT department

- **File organiser:** tidy shared drives and download folders.
- **Log analyser:** spot repeated failed logins and suspicious IP addresses quickly.
- **Health checker:** run on a schedule to catch full disks, high memory use or stopped services before users notice.
- **Data validator:** clean up messy CSV exports (e.g. user or device lists) before importing them elsewhere.
- **Report generator / main.py:** produce one combined, shareable report after a routine automated sweep.

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

The GitHub Actions pipeline described above implements container build, scanning,
publishing and batch deployment to a Linux Docker host. The broader deployment
layout is:

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
