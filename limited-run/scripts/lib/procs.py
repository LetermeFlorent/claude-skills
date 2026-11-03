import os
from pathlib import Path

from common import WINDOWS

STAT_START_FIELD = 19
UNKNOWN_START = 0


def parse_start(stat_text):
    fields = stat_text.rsplit(")", 1)[-1].split()
    return int(fields[STAT_START_FIELD]) if len(fields) > STAT_START_FIELD else UNKNOWN_START


def _posix_identity(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return None
    except PermissionError:
        pass
    try:
        return parse_start(Path(f"/proc/{pid}/stat").read_text(encoding="ascii"))
    except (OSError, ValueError):
        return UNKNOWN_START


def identity(pid):
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return None
    if WINDOWS:
        import winapi
        return winapi.identity(pid)
    return _posix_identity(pid)


def same(pid, created):
    found = identity(pid)
    return found is not None and found == created
