import ctypes
import os
import sys
import time
from ctypes import wintypes
from pathlib import Path

sys.dont_write_bytecode = True

from core.processes import as_list, powershell, process_table

LOAD = "Import-Module VirtualDesktop -WarningAction SilentlyContinue; "
user32 = ctypes.WinDLL("user32", use_last_error=True)
ENUM_PROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def windows_of(pid):
    found = []

    def visit(handle, _):
        owner = wintypes.DWORD()
        user32.GetWindowThreadProcessId(handle, ctypes.byref(owner))
        if owner.value == pid and user32.IsWindowVisible(handle):
            title = ctypes.create_unicode_buffer(512)
            user32.GetWindowTextW(handle, title, 512)
            if title.value:
                found.append((handle, title.value))
        return True

    user32.EnumWindows(ENUM_PROC(visit), 0)
    return found


def maximize(pid):
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        found = windows_of(pid)
        if found:
            handle = found[0][0]
            area = wintypes.RECT()
            user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(area), 0)
            user32.ShowWindow(handle, 9)
            user32.MoveWindow(handle, area.left, area.top, area.right - area.left, area.bottom - area.top, True)
            user32.ShowWindow(handle, 3)
            return handle
        time.sleep(0.5)
    return None


def desktops_of(handles):
    listed = ",".join(str(handle) for handle in handles)
    script = (LOAD + f"@({listed}) | ForEach-Object {{ Get-DesktopFromWindow ([IntPtr]$_) | Get-DesktopIndex }}"
              " | ConvertTo-Json -Compress")
    return sorted(set(as_list(powershell(script))))


def host_desktop(work_folder):
    entries = {entry["ProcessId"]: entry for entry in process_table()}
    name = Path(work_folder).name.lower()
    current = os.getpid()
    for _ in range(15):
        entry = entries.get(current)
        if not entry or (entry.get("Name") or "").lower() == "explorer.exe":
            return None
        found = windows_of(current)
        if found:
            handles = [handle for handle, title in found if len(found) == 1 or name in title.lower()]
            desks = desktops_of(handles) if handles else []
            return desks[0] if len(desks) == 1 else None
        current = entry["ParentProcessId"]
    return None


def pick_desktop(choice):
    if choice == "current" or powershell("[bool](Get-Module -ListAvailable VirtualDesktop)") != "True":
        return None
    if choice is not None:
        return int(choice)
    return host_desktop(os.getcwd())


def show(pid, desktop):
    handle = maximize(pid)
    if handle is None:
        return "window not found within the wait, left where Chrome opened it"
    if desktop is None:
        return "window maximized on the primary screen, on the desktop shown now"
    powershell(LOAD + f"Move-Window -Desktop (Get-Desktop {desktop}) -Hwnd ([IntPtr]{handle}) | Out-Null")
    return f"window maximized on the primary screen, virtual desktop {desktop}"
