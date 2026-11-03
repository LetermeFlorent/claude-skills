import os
import time

KB_PER_GB = 1024 ** 2
PERCENT = 100.0
MS_PER_SECOND = 1000.0
IDLE_FIELDS = (3, 4)
STAT_FIELDS = 8
NAME_FIELD, TICKS_FIELD = 2, 12
VIRTUAL = ("loop", "ram", "zram", "fd", "sr", "dm-", "md")
ENCODING = "utf-8"


def read(path):
    try:
        with open(path, encoding=ENCODING) as handle:
            return handle.read()
    except OSError:
        return ""


def available_gb(meminfo):
    for line in meminfo.splitlines():
        fields = line.split()
        if len(fields) > 1 and fields[0] == "MemAvailable:" and fields[1].isdigit():
            return int(fields[1]) / KB_PER_GB
    return None


def cpu_ticks(stat):
    for line in stat.splitlines():
        fields = line.split()
        if fields and fields[0] == "cpu" and all(field.isdigit() for field in fields[1:STAT_FIELDS + 1]):
            values = [int(field) for field in fields[1:STAT_FIELDS + 1]]
            return sum(values[index] for index in IDLE_FIELDS), sum(values)
    return None


def cpu_busy(first, second):
    if not first or not second:
        return None
    idle, total = second[0] - first[0], second[1] - first[1]
    return PERCENT * (total - idle) / total if total > 0 else None


def is_whole_disk(name):
    return not name.startswith(VIRTUAL) and os.path.isdir(f"/sys/block/{name}")


def disk_ticks(diskstats, whole):
    ticks = {}
    for line in diskstats.splitlines():
        fields = line.split()
        if len(fields) > TICKS_FIELD and fields[TICKS_FIELD].isdigit() and whole(fields[NAME_FIELD]):
            ticks[fields[NAME_FIELD]] = int(fields[TICKS_FIELD])
    return ticks


def disk_busy(first, second, elapsed):
    if elapsed <= 0:
        return None
    shares = [PERCENT * (second[name] - first[name]) / (elapsed * MS_PER_SECOND) for name in second if name in first]
    return max(shares) if shares else None


def sample(window):
    ram = available_gb(read("/proc/meminfo"))
    cpu_before, disk_before = cpu_ticks(read("/proc/stat")), disk_ticks(read("/proc/diskstats"), is_whole_disk)
    start = time.monotonic()
    time.sleep(window)
    cpu_after, disk_after = cpu_ticks(read("/proc/stat")), disk_ticks(read("/proc/diskstats"), is_whole_disk)
    elapsed = time.monotonic() - start
    return ram, cpu_busy(cpu_before, cpu_after), disk_busy(disk_before, disk_after, elapsed)
