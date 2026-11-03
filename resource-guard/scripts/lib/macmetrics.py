import os
import re
import subprocess

BYTES_PER_GB = 1024 ** 3
PERCENT = 100.0
VM_STAT_TIMEOUT = 10
PAGE_SIZE = re.compile(r"page size of (\d+) bytes")
FREE_PAGES = re.compile(r"^Pages (?:free|inactive):\s+(\d+)", re.MULTILINE)


def free_gb(vm_stat):
    size, counts = PAGE_SIZE.search(vm_stat), FREE_PAGES.findall(vm_stat)
    if not size or not counts:
        return None
    return int(size.group(1)) * sum(int(count) for count in counts) / BYTES_PER_GB


def load_percent(load, cpus):
    return PERCENT * load / cpus if cpus else None


def sample(window):
    try:
        done = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=VM_STAT_TIMEOUT)
        ram = free_gb(done.stdout)
    except (OSError, subprocess.SubprocessError):
        ram = None
    try:
        cpu = load_percent(os.getloadavg()[0], os.cpu_count())
    except OSError:
        cpu = None
    return ram, cpu, None
