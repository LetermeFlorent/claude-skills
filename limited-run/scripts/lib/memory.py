import os
import re
from pathlib import Path

from common import WINDOWS

MIN_MB, MAX_MB, UNKNOWN_MB = 512, 4096, 1024
SHARE = 2
KB_PER_MB = 1024
MEMINFO = Path("/proc/meminfo")
AVAILABLE = re.compile(r"^MemAvailable:\s+(\d+)\s+kB", re.MULTILINE)


def cap_mb(free):
    if free is None:
        return UNKNOWN_MB
    return max(MIN_MB, min(MAX_MB, free // SHARE))


def parse_meminfo(text):
    found = AVAILABLE.search(text)
    return int(found.group(1)) // KB_PER_MB if found else None


def _sysconf_free():
    try:
        return os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE") // (KB_PER_MB * KB_PER_MB)
    except (ValueError, OSError, AttributeError):
        return None


def free_mb():
    if WINDOWS:
        import winapi
        return winapi.free_mb()
    try:
        return parse_meminfo(MEMINFO.read_text(encoding="ascii")) or _sysconf_free()
    except OSError:
        return _sysconf_free()
