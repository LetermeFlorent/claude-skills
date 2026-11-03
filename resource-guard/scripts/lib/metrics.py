import importlib
import shutil
import sys
from pathlib import Path

WINDOW_SECONDS = 0.5
BYTES_PER_GB = 1024 ** 3
PLATFORMS = (("win", "winmetrics"), ("linux", "linuxmetrics"), ("darwin", "macmetrics"))
NOTHING = (None, None, None)
ROOT = "/"


def platform_module():
    for prefix, name in PLATFORMS:
        if sys.platform.startswith(prefix):
            return importlib.import_module(name)
    return None


def free_space(folder=None):
    anchor = Path(folder or Path.cwd()).resolve().anchor or ROOT
    try:
        free = shutil.disk_usage(anchor).free / BYTES_PER_GB
    except OSError:
        free = None
    return anchor.rstrip("\\/") or ROOT, free


def sample():
    module = platform_module()
    try:
        ram, cpu, disk = module.sample(WINDOW_SECONDS) if module else NOTHING
    except (OSError, ValueError, AttributeError):
        ram, cpu, disk = NOTHING
    drive, free = free_space()
    return {"ram_gb": ram, "cpu": cpu, "disk": disk, "drive": drive, "free_gb": free}
