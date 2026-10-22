import ctypes
import time
from ctypes import wintypes

from core.common import POLL_STEP

SW_MAXIMIZE = 3
SW_RESTORE = 9
SPI_GETWORKAREA = 0x0030
TITLE_LIMIT = 512
WINDOW_WAIT = 10

user32 = ctypes.WinDLL("user32", use_last_error=True)
ENUM_PROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def windows_of(pid):
    found = []

    def visit(handle, _):
        owner = wintypes.DWORD()
        user32.GetWindowThreadProcessId(handle, ctypes.byref(owner))
        if owner.value == pid and user32.IsWindowVisible(handle):
            title = ctypes.create_unicode_buffer(TITLE_LIMIT)
            user32.GetWindowTextW(handle, title, TITLE_LIMIT)
            if title.value:
                found.append((handle, title.value))
        return True

    user32.EnumWindows(ENUM_PROC(visit), 0)
    return found


def work_area():
    rect = wintypes.RECT()
    user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top


def maximize(pid):
    deadline = time.monotonic() + WINDOW_WAIT
    while time.monotonic() < deadline:
        found = windows_of(pid)
        if found:
            handle = found[0][0]
            user32.ShowWindow(handle, SW_RESTORE)
            user32.MoveWindow(handle, *work_area(), True)
            user32.ShowWindow(handle, SW_MAXIMIZE)
            return handle
        time.sleep(POLL_STEP)
    return None
