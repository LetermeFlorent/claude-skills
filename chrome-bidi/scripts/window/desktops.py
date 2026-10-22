import os
import sys
from pathlib import Path

from core.processes import as_list, powershell, table
from window.placement import maximize, windows_of

MODULE = "VirtualDesktop"
LOAD = f"Import-Module {MODULE} -WarningAction SilentlyContinue; "
WALK_LIMIT = 15
SHELL_ROOT = "explorer.exe"
CURRENT = "current"
EXIT_ASK = 2
POWERSHELL_TRUE = "True"


def module_present():
    return powershell(f"[bool](Get-Module -ListAvailable {MODULE})") == POWERSHELL_TRUE


def desktops_of(handles):
    listed = ",".join(str(handle) for handle in handles)
    script = (LOAD + f"@({listed}) | ForEach-Object {{ Get-DesktopFromWindow ([IntPtr]$_) | Get-DesktopIndex }}"
              " | ConvertTo-Json -Compress")
    return sorted(set(as_list(powershell(script))))


def desktop_list():
    return as_list(powershell(LOAD + "Get-DesktopList | Select-Object Number,Name,Visible | ConvertTo-Json -Compress"))


def move(handle, index):
    powershell(LOAD + f"Move-Window -Desktop (Get-Desktop {index}) -Hwnd ([IntPtr]{handle}) | Out-Null")


def host_desktop(work_folder):
    entries = {entry["ProcessId"]: entry for entry in table()}
    name = Path(work_folder).name.lower()
    current = os.getpid()
    for _ in range(WALK_LIMIT):
        entry = entries.get(current)
        if not entry or (entry.get("Name") or "").lower() == SHELL_ROOT:
            return None
        found = windows_of(current)
        if found:
            handles = [handle for handle, title in found if len(found) == 1 or name in title.lower()]
            desks = desktops_of(handles) if handles else []
            return desks[0] if len(desks) == 1 else None
        current = entry["ParentProcessId"]
    return None


def pick_desktop(choice):
    if choice == CURRENT:
        return None
    if not module_present():
        print(f"VIRTUAL_DESKTOP_MODULE_MISSING: ask the user to install it (Install-Module {MODULE} -Scope "
              "CurrentUser -Force) or to accept --desktop current")
        sys.exit(EXIT_ASK)
    if choice is not None:
        return int(choice)
    found = host_desktop(os.getcwd())
    if found is None:
        print("HOST_DESKTOP_UNKNOWN: ask the user which virtual desktop, then run again with --desktop <n>")
        for desk in desktop_list():
            print(f"  desktop {desk.get('Number')}: {desk.get('Name')}{' (shown now)' if desk.get('Visible') else ''}")
        sys.exit(EXIT_ASK)
    return found


def show(pid, desktop):
    handle = maximize(pid)
    if handle is None:
        return "window not found within the wait, left where Chrome opened it"
    if desktop is None:
        return "window maximized on the primary screen, on the desktop shown now"
    move(handle, desktop)
    return f"window maximized on the primary screen, virtual desktop {desktop}"
