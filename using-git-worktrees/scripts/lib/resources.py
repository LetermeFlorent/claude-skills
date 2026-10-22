from common import run

MIN_FREE_MB = 1500
MAX_CPU = 85
FULL_WORKERS = 2
POWERSHELL_TIMEOUT = 60
PROBE = (
    "$o=Get-CimInstance Win32_OperatingSystem;$c=(Get-CimInstance Win32_Processor).LoadPercentage;"
    "$d=Get-CimInstance Win32_LogicalDisk -Filter \"DeviceID='C:'\";"
    "Write-Output ('{0} {1} {2}' -f $o.FreePhysicalMemory,$c,$d.FreeSpace)"
)
KB_PER_MB = 1024
BYTES_PER_GB = 1024 ** 3
MIN_HEAP_MB = 512
MAX_HEAP_MB = 4096


def parse_probe(text):
    fields = text.split()
    if len(fields) != 3 or not all(field.isdigit() for field in fields):
        return None
    free_kb, cpu, disk = (int(field) for field in fields)
    return {"free_mb": free_kb // KB_PER_MB, "cpu": cpu, "disk_gb": disk // BYTES_PER_GB}


def probe(cwd):
    code, out, _ = run(["powershell", "-NoProfile", "-Command", PROBE], cwd, POWERSHELL_TIMEOUT)
    return parse_probe(out) if code == 0 else None


def workers_for(free_mb, cpu):
    if free_mb < MIN_FREE_MB:
        return 0
    return 1 if cpu > MAX_CPU else FULL_WORKERS


def heap_mb(free_mb):
    return max(MIN_HEAP_MB, min(MAX_HEAP_MB, free_mb // 3))
