import math
import os

from common import TOOL

DEFAULTS = {"ram_gb": 1.5, "cpu": 85.0, "disk": 100.0, "timeout": 300.0, "free_gb": 20.0}
ENV_NAMES = {
    "ram_gb": "RESOURCE_GUARD_RAM_GB",
    "cpu": "RESOURCE_GUARD_CPU",
    "disk": "RESOURCE_GUARD_DISK",
    "timeout": "RESOURCE_GUARD_TIMEOUT",
    "free_gb": "RESOURCE_GUARD_FREE_GB",
}
UNKNOWN = "unknown"


def _number(text):
    try:
        value = float(text)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) and value >= 0 else None


def resolve(flags=None, environ=None):
    flags = flags or {}
    environ = os.environ if environ is None else environ
    chosen = {}
    for key, default in DEFAULTS.items():
        flag, env = flags.get(key), _number(environ.get(ENV_NAMES[key]))
        chosen[key] = flag if flag is not None else env if env is not None else default
    return chosen


def reasons(sample, chosen):
    ram, cpu, disk = sample.get("ram_gb"), sample.get("cpu"), sample.get("disk")
    found = []
    if ram is not None and ram < chosen["ram_gb"]:
        found.append(f"ram {ram:.1f} GB < {chosen['ram_gb']:g} GB")
    if cpu is not None and cpu > chosen["cpu"]:
        found.append(f"cpu {cpu:.0f} % > {chosen['cpu']:g} %")
    if disk is not None and disk > chosen["disk"]:
        found.append(f"disk {disk:.0f} % busy > {chosen['disk']:g} %")
    return found


def low_disk(sample, chosen):
    free = sample.get("free_gb")
    return free is not None and free < chosen["free_gb"]


def _shown(value, pattern):
    return UNKNOWN if value is None else pattern.format(value)


def describe(sample):
    return ", ".join((
        "ram " + _shown(sample.get("ram_gb"), "{:.1f} GB free"),
        "cpu " + _shown(sample.get("cpu"), "{:.0f} %"),
        "disk " + _shown(sample.get("disk"), "{:.0f} % busy"),
        f"{sample.get('drive') or '?'} " + _shown(sample.get("free_gb"), "{:.0f} GB free"),
    ))


def status_line(sample, found):
    verdict = f"wait ({', '.join(found)})" if found else "ok"
    return f"{TOOL}: {describe(sample)}: {verdict}"


def disk_warning(sample, chosen):
    return (f"{TOOL}: warning: {sample.get('drive')} has {sample['free_gb']:.0f} GB free, under "
            f"{chosen['free_gb']:g} GB; waiting does not free disk, delete leftovers instead")
