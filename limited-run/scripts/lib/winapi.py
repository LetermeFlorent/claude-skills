import ctypes
from ctypes import wintypes

from common import MB

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
ntdll = ctypes.WinDLL("ntdll")
HANDLE, DWORD, BOOL = wintypes.HANDLE, wintypes.DWORD, wintypes.BOOL
QUERY_LIMITED = 0x1000
ADOPT_ACCESS = 0x0100 | 0x0001 | 0x0800
STILL_ACTIVE = 259
EXTENDED_LIMIT_INFORMATION = 9
LIMIT_PRIORITY_CLASS, LIMIT_JOB_MEMORY, LIMIT_KILL_ON_CLOSE = 0x20, 0x200, 0x2000
BELOW_NORMAL = 0x4000
STATUS_MASK = 0xFFFFFFFF
TIMES = 4
KILLED_EXIT_CODE = 1


class IoCounters(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint64) for name in (
        "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
        "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]


class BasicLimits(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                ("LimitFlags", DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", DWORD),
                ("Affinity", ctypes.c_size_t), ("PriorityClass", DWORD), ("SchedulingClass", DWORD)]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [("BasicLimitInformation", BasicLimits), ("IoInfo", IoCounters),
                ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]


class MemoryStatus(ctypes.Structure):
    _fields_ = [("dwLength", DWORD), ("dwMemoryLoad", DWORD)] + [(name, ctypes.c_uint64) for name in (
        "ullTotalPhys", "ullAvailPhys", "ullTotalPageFile", "ullAvailPageFile",
        "ullTotalVirtual", "ullAvailVirtual", "ullAvailExtendedVirtual")]


def _declare(function, arguments, result):
    function.argtypes, function.restype = arguments, result


_declare(kernel32.CreateJobObjectW, [ctypes.c_void_p, wintypes.LPCWSTR], HANDLE)
_declare(kernel32.SetInformationJobObject, [HANDLE, ctypes.c_int, ctypes.c_void_p, DWORD], BOOL)
_declare(kernel32.AssignProcessToJobObject, [HANDLE, HANDLE], BOOL)
_declare(kernel32.TerminateJobObject, [HANDLE, wintypes.UINT], BOOL)
_declare(kernel32.CloseHandle, [HANDLE], BOOL)
_declare(kernel32.OpenProcess, [DWORD, BOOL, DWORD], HANDLE)
_declare(kernel32.GetExitCodeProcess, [HANDLE, ctypes.POINTER(DWORD)], BOOL)
_declare(kernel32.GetProcessTimes, [HANDLE] + [ctypes.POINTER(ctypes.c_uint64)] * TIMES, BOOL)
_declare(kernel32.GlobalMemoryStatusEx, [ctypes.POINTER(MemoryStatus)], BOOL)
_declare(ntdll.NtResumeProcess, [HANDLE], ctypes.c_long)


def check(ok, what):
    if not ok:
        raise ctypes.WinError(ctypes.get_last_error(), f"{what} failed")


def free_mb():
    status = MemoryStatus()
    status.dwLength = ctypes.sizeof(MemoryStatus)
    return status.ullAvailPhys // MB if kernel32.GlobalMemoryStatusEx(ctypes.byref(status)) else None


def identity(pid):
    handle = kernel32.OpenProcess(QUERY_LIMITED, False, pid)
    if not handle:
        return None
    try:
        code, times = DWORD(), [ctypes.c_uint64() for _ in range(TIMES)]
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value != STILL_ACTIVE:
            return None
        if not kernel32.GetProcessTimes(handle, *(ctypes.byref(time) for time in times)):
            return None
        return times[0].value
    finally:
        kernel32.CloseHandle(handle)


def create_job(cap_mb):
    job = kernel32.CreateJobObjectW(None, None)
    check(job, "CreateJobObject")
    limits = ExtendedLimits()
    basic = limits.BasicLimitInformation
    basic.LimitFlags = LIMIT_PRIORITY_CLASS | LIMIT_KILL_ON_CLOSE | (LIMIT_JOB_MEMORY if cap_mb else 0)
    basic.PriorityClass = BELOW_NORMAL
    limits.JobMemoryLimit = cap_mb * MB
    done = kernel32.SetInformationJobObject(job, EXTENDED_LIMIT_INFORMATION, ctypes.byref(limits),
                                            ctypes.sizeof(limits))
    if not done:
        error = ctypes.get_last_error()
        kernel32.CloseHandle(job)
        raise ctypes.WinError(error, "SetInformationJobObject failed")
    return job


def adopt_and_resume(job, pid):
    process = kernel32.OpenProcess(ADOPT_ACCESS, False, pid)
    check(process, "OpenProcess")
    try:
        check(kernel32.AssignProcessToJobObject(job, process), "AssignProcessToJobObject")
        status = ntdll.NtResumeProcess(process)
        if status:
            raise OSError(f"NtResumeProcess failed with status {status & STATUS_MASK:#010x}")
    finally:
        kernel32.CloseHandle(process)


def terminate_job(job):
    kernel32.TerminateJobObject(job, KILLED_EXIT_CODE)


def close_job(job):
    kernel32.CloseHandle(job)
