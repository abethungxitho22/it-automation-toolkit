# Performance Log

Record every slow or resource-heavy operation you investigate.

## The method

1. **Measure first.** Never guess. Time it (and check memory if relevant).
2. **Find the bottleneck.** Which line or function uses the most time or memory?
3. **Form a hypothesis.** "This is slow because ___."
4. **Change one thing**, then measure again.
5. **Compare before and after.** Keep the numbers.
6. **Check the answer is still correct.** A faster wrong answer is worse than a slow right one.

---

## Health checker (measure_health_checker.py)

- **Slowest check:** The process check (check_process).
- **Its average time and share of the total:** About 1,353 ms on average
  (min 1,044 ms, max 1,825 ms), which is roughly 100% of the total run time.
  Disk averaged 0.36 ms and memory 0.60 ms.
- **Why I think it is slow:** The time is not spent in my Python code. The check
  starts a separate Windows program (tasklist) and waits while Windows collects
  a list of every running process. Disk and memory ask Windows one simple
  question directly, so they are almost instant.
- **Could it be improved? How?** TODO: run `Measure-Command { tasklist }` and
  `Measure-Command { tasklist /FI "IMAGENAME eq chrome.exe" /NH }` two or three
  times each, then write: "tasklist took ___ ms and the filtered version took
  ___ ms, so filtering (helped / made no real difference)." The process check
  only runs when --process is used, so a default run is still fast. For a check
  that runs once an hour, about 1.4 seconds is acceptable.

## slow1_duplicate_ips.py

- **Before (time):** About 2.5 to 3 seconds.
- **Bottleneck (function / line):** find_duplicates (about 99% of the time in cProfile).
- **Why it is slow:** The `in` check on a list compares against items one by one,
  and it ran 16,000 times on lists holding thousands of addresses.
- **Fix:** Replaced the two lists with sets (set() and .add instead of [] and .append).
- **After (time):** 0.01 seconds.
- **Still gives the same answer?** Yes, 8000 duplicates before and after.

## slow2_cpu_alerts.py

- **Before (time):** About 2.7 seconds.
- **Bottleneck (function / line):** find_high_readings, the line inside the loop
  that sorts the whole list on every pass.
- **Why it is slow:** The highest reading never changes, but the script sorted
  4,000 numbers 4,000 times.
- **Fix:** Worked out the highest reading once before the loop using max().
- **After (time):** 0.00 seconds
- **Still gives the same answer? Yes

## slow3_memory_reader.py

- **Before (time and peak memory):** 0.77 seconds and 48.4 MB peak memory (16.1 MB file).
- **Bottleneck:** count_errors loaded the whole file and built a list of all 300,000 lines.
- **Why it uses so much memory:** read().splitlines() keeps the whole file and every
  line in memory at once, about three times the file size.
- **Fix:** Looped over the open file directly (for line in log_file), so only one
  line is in memory at a time.
- **After (time and peak memory):** About 0.9 seconds (no real change, within normal
  variation) and 0.1 MB peak memory.
- **Still gives the same answer?** Yes, 30000 errors before and after.
## Reliability: the growing log file

- **The problem:** health_check.log is appended to on every run and never
  shrinks. On a server running the checker regularly, it would eventually fill
  the disk, so the tool meant to warn about full disks could cause one.
- **My fix:** TODO: describe the change you made to setup_logging().
- **How I tested it:** TODO: for example, that all 19 tests still pass and how
  you confirmed the log file stays capped.