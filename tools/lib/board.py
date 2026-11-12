"""Progress board: starts its local server now and at every login, so the page survives a restart."""
import os
import subprocess
import sys
from pathlib import Path

FOLDER = "progress-board"
NAME = "claude-skills-progress-board"
LABEL = "progress-board"


def server_file(repo):
    return Path(repo) / FOLDER / "server.py"


def python_quiet():
    """pythonw on Windows starts without a console window."""
    exe = Path(sys.executable)
    quiet = exe.with_name("pythonw.exe")
    return quiet if os.name == "nt" and quiet.exists() else exe


def autostart_file(home=None):
    home = Path(home or Path.home())
    if sys.platform == "darwin":
        return home / "Library" / "LaunchAgents" / f"{NAME}.plist"
    return Path(os.environ.get("XDG_CONFIG_HOME") or home / ".config") / "autostart" / f"{NAME}.desktop"


def autostart_text(command):
    if sys.platform == "darwin":
        args = "".join(f"<string>{a}</string>" for a in command)
        return ('<?xml version="1.0" encoding="UTF-8"?>\n<plist version="1.0"><dict>'
                f"<key>Label</key><string>{NAME}</string><key>ProgramArguments</key><array>{args}</array>"
                "<key>RunAtLoad</key><true/></dict></plist>\n")
    return "[Desktop Entry]\nType=Application\nName=Progress board\nExec=" + " ".join(f'"{a}"' for a in command) + "\nNoDisplay=true\n"


def set_autostart(command):
    if os.name == "nt":
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, NAME, 0, winreg.REG_SZ, subprocess.list2cmdline(command))
        return
    path = autostart_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(autostart_text(command), encoding="utf-8")


def drop_autostart():
    if os.name == "nt":
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
            try:
                winreg.DeleteValue(key, NAME)
            except FileNotFoundError:
                pass
        return
    autostart_file().unlink(missing_ok=True)


def sync_board(repo):
    server = server_file(repo)
    if not server.is_file():
        return []
    command = [str(python_quiet()), "-I", str(server)]
    try:
        set_autostart(command)
    except OSError as error:
        return [(False, f"{LABEL}: start at login not set ({error})")]
    done = subprocess.run([sys.executable, "-I", str(server), "start"], capture_output=True, text=True)
    if done.returncode:
        return [(False, f"{LABEL}: {(done.stderr or done.stdout).strip()}")]
    return [(True, f"{LABEL}: {done.stdout.strip()}, starts at every login")]


def unsync_board(repo):
    if not server_file(repo).is_file():
        return []
    try:
        drop_autostart()
    except OSError as error:
        return [(False, f"{LABEL}: start at login not removed ({error})")]
    return [(True, f"{LABEL}: no longer starts at login, the running server stops at the next restart")]
