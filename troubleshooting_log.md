# Troubleshooting Log

Use this log for every problem you investigate this week. It becomes the
basis of your debugging report and your Scrum demonstration.

## The method (follow it in order)

1. **Reproduce it.** Run the script yourself and see the problem happen.
2. **Read the error.** Start with the LAST line of the message (the error type),
   then the line number just above it.
3. **Isolate it.** Which line, and which input, causes it?
4. **Form a hypothesis.** "I think the cause is ___ because ___."
5. **Test one change at a time.** Change one thing, run it, see what happens.
6. **Fix the root cause**, not just the symptom.
7. **Prevent it.** Add a test, a check, or a clearer error message.

---

## Problem 1: bug1_disk_report.py

- **Symptom (what I saw):**
- **Error message / type:**
- **What I tried:**
- **Root cause:**
- **Fix:**
- **How to prevent it:**

## Problem 2: bug2_system_summary.py

- **Symptom (what I saw):**
- **Error message / type:**
- **What I tried:**
- **Root cause:**
- **Fix:**
- **How to prevent it:**

## Problem 3: bug3_error_counter.py

- **Symptom (what I saw):**
- **Error message / type:**
- **What I tried:**
- **Root cause:**
- **Fix:**
- **How to prevent it:**

## Problem 4: bug4_user_import.py

- **Symptom (what I saw):**
- **Error message / type:**
- **What I tried:**
- **Root cause:**
- **Fix:**
- **How to prevent it:**

## Problem 5: bug5_server_list.py

- **Symptom (what I saw):**
- **Error message / type:**
- **What I tried:**
- **Root cause:**
- **Fix:**
- **How to prevent it:**

---

## Problem from my own project: health checker crash

- **Symptom (what I saw):** Tests crashed with a UnicodeDecodeError, then an AttributeError.
- **Error message / type:** `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff`, then `'NoneType' object has no attribute 'lower'`
- **What I tried:** Read the traceback from the bottom up and traced the second error back to the first.
- **Root cause:** Windows `tasklist` prints bytes that are not valid UTF-8, so reading the output failed and left `stdout` empty.
- **Fix:** A shared `run_command()` helper that decodes with `errors="replace"`.
- **How to prevent it:** A regression test that feeds the helper an undecodable byte.
