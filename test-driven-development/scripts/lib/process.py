import os
import shutil
import subprocess

from common import DECODE_ERRORS, ENCODING

WINDOWS = os.name == "nt"
LOW_PRIORITY = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)
NICENESS = 10
KILL_TREE = ("taskkill", "/T", "/F", "/PID")
KILL_TIMEOUT = 30
PROBE_TIMEOUT = 60
KB_PER_MB = 1024
BYTES_PER_GB = 1024 ** 3
DEFAULT_DRIVE = "C:"
PROBE = ("$o = Get-CimInstance Win32_OperatingSystem; "
         "$c = (Get-CimInstance Win32_Processor | Measure-Object LoadPercentage -Average).Average; "
         "$d = Get-CimInstance Win32_LogicalDisk -Filter \"DeviceID='{drive}'\"; "
         "\"$($o.FreePhysicalMemory) $c $($d.FreeSpace)\"")


def _lower_priority():
    os.nice(NICENESS)


def _priority():
    return {"creationflags": LOW_PRIORITY} if WINDOWS else {"preexec_fn": _lower_priority}


def _decode(raw):
    return (raw or b"").decode(ENCODING, errors=DECODE_ERRORS)


def _stop(process):
    if WINDOWS:
        subprocess.run([*KILL_TREE, str(process.pid)], capture_output=True, timeout=KILL_TIMEOUT)
    else:
        process.kill()


def execute(command, root, extra_env, timeout):
    program = shutil.which(command[0]) or command[0]
    try:
        process = subprocess.Popen([program, *command[1:]], cwd=str(root), stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   env={**os.environ, **extra_env}, **_priority())
    except FileNotFoundError as error:
        raise LookupError(f"{command[0]} is not installed or not on PATH") from error
    try:
        raw, _ = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _stop(process)
        return None, _drain(process)
    return process.returncode, _decode(raw)


def _drain(process):
    try:
        raw, _ = process.communicate(timeout=KILL_TIMEOUT)
    except subprocess.TimeoutExpired:
        return ""
    return _decode(raw)


def resources(root):
    if not WINDOWS:
        return None
    drive = root.drive or DEFAULT_DRIVE
    try:
        done = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", PROBE.format(drive=drive)],
                              capture_output=True, text=True, timeout=PROBE_TIMEOUT)
        free_kb, cpu, disk = (float(value) for value in done.stdout.split())
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None
    return free_kb / KB_PER_MB, cpu, disk / BYTES_PER_GB
