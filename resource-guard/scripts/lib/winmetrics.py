import ctypes
import time
from ctypes import wintypes

BYTES_PER_GB = 1024 ** 3
PERCENT = 100.0
SUCCESS = 0
VALID_STATUSES = (0, 1)
PDH_FMT_DOUBLE = 0x00000200
PDH_FMT_NOCAP100 = 0x00008000
HIGH_SHIFT = 32
CPU_COUNTER = "\\Processor(_Total)\\% Processor Time"
DISK_COUNTER = "\\PhysicalDisk(_Total)\\% Disk Time"
HANDLE = ctypes.c_void_p
MEMORY_FIELDS = ("total_phys", "avail_phys", "total_page", "avail_page", "total_virtual", "avail_virtual", "extended")


class MemoryStatus(ctypes.Structure):
    _fields_ = [("length", wintypes.DWORD), ("load", wintypes.DWORD)]
    _fields_ += [(name, ctypes.c_ulonglong) for name in MEMORY_FIELDS]


class CounterValue(ctypes.Structure):
    _fields_ = [("status", wintypes.DWORD), ("value", ctypes.c_double)]


def free_ram_gb():
    status = MemoryStatus()
    status.length = ctypes.sizeof(MemoryStatus)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        return None
    return status.avail_phys / BYTES_PER_GB


def _pdh():
    pdh = ctypes.WinDLL("pdh")
    pdh.PdhOpenQueryW.argtypes = [wintypes.LPCWSTR, ctypes.c_size_t, ctypes.POINTER(HANDLE)]
    pdh.PdhAddEnglishCounterW.argtypes = [HANDLE, wintypes.LPCWSTR, ctypes.c_size_t, ctypes.POINTER(HANDLE)]
    pdh.PdhCollectQueryData.argtypes = [HANDLE]
    pdh.PdhGetFormattedCounterValue.argtypes = [
        HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(CounterValue)]
    pdh.PdhCloseQuery.argtypes = [HANDLE]
    for function in (pdh.PdhOpenQueryW, pdh.PdhAddEnglishCounterW, pdh.PdhCollectQueryData,
                     pdh.PdhGetFormattedCounterValue, pdh.PdhCloseQuery):
        function.restype = ctypes.c_long
    return pdh


def _value(pdh, counter, flags):
    value = CounterValue()
    if pdh.PdhGetFormattedCounterValue(counter, flags, None, ctypes.byref(value)) != SUCCESS:
        return None
    return value.value if value.status in VALID_STATUSES else None


def _collect(pdh, query, window):
    cpu, disk = HANDLE(), HANDLE()
    if pdh.PdhAddEnglishCounterW(query, CPU_COUNTER, 0, ctypes.byref(cpu)) != SUCCESS:
        return None
    has_disk = pdh.PdhAddEnglishCounterW(query, DISK_COUNTER, 0, ctypes.byref(disk)) == SUCCESS
    pdh.PdhCollectQueryData(query)
    time.sleep(window)
    if pdh.PdhCollectQueryData(query) != SUCCESS:
        return None
    busy = _value(pdh, cpu, PDH_FMT_DOUBLE)
    if busy is None:
        return None
    return busy, _value(pdh, disk, PDH_FMT_DOUBLE | PDH_FMT_NOCAP100) if has_disk else None


def pdh_busy(window):
    pdh = _pdh()
    query = HANDLE()
    if pdh.PdhOpenQueryW(None, 0, ctypes.byref(query)) != SUCCESS:
        return None
    try:
        return _collect(pdh, query, window)
    finally:
        pdh.PdhCloseQuery(query)


def _times():
    idle, kernel, user = wintypes.FILETIME(), wintypes.FILETIME(), wintypes.FILETIME()
    if not ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)):
        return None
    return tuple(part.dwHighDateTime << HIGH_SHIFT | part.dwLowDateTime for part in (idle, kernel, user))


def cpu_from_times(first, second):
    if not first or not second:
        return None
    idle, kernel, user = (after - before for before, after in zip(first, second))
    total = kernel + user
    return PERCENT * (total - idle) / total if total > 0 else None


def sample(window):
    ram = free_ram_gb()
    try:
        busy = pdh_busy(window)
    except (OSError, AttributeError):
        busy = None
    if busy is not None:
        return (ram, *busy)
    first = _times()
    time.sleep(window)
    return ram, cpu_from_times(first, _times()), None
