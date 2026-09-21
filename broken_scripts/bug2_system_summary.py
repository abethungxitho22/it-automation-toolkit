import platform
import os


def show_summary():
    cpus = os.cpu_count()
    system = platform.system()
    print("Operating system: " + system)
    print("CPU cores: " + str(cpus))


show_summary()
