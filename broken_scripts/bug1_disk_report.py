import shutil


def report_disk(path):
    usage = shutil.disk_usage(path)
    percent_used = usage.used / usage.total * 100
    print("Disk usage for", path, ":", round(percent_used, 1), "%")


report_disk(".")
