def count_errors(lines):
    count = 0
    for line in lines:
     if "ERROR" in line:
        count += 1
    return count


log_lines = [
    "ERROR Disk full on server-01",
    "INFO Backup completed",
    "ERROR Failed login for admin",
    "WARNING High memory usage",
    "INFO Service restarted",
]

print("Errors found:", count_errors(log_lines))
print("Expected: 2")
