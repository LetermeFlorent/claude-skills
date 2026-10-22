import os
import stat
import subprocess
from pathlib import Path

WINDOWS = os.name == "nt"
MOUNT_POINT = getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003)
TIMEOUT = 20
EXTENDED_PREFIX = "\\\\?\\"


def is_link(path):
    try:
        info = os.lstat(path)
    except OSError:
        return False
    if stat.S_ISLNK(info.st_mode):
        return True
    return getattr(info, "st_reparse_tag", 0) == MOUNT_POINT


def same_path(first, second):
    return os.path.normcase(os.path.realpath(first)) == os.path.normcase(os.path.realpath(second))


def _plain(path):
    text = os.fspath(path)
    text = text[len(EXTENDED_PREFIX):] if text.startswith(EXTENDED_PREFIX) else text
    return os.path.normcase(os.path.normpath(text))


def points_at(link, target):
    try:
        written = os.readlink(link)
    except OSError:
        return False
    reached = os.path.join(os.path.dirname(link), written)
    return _plain(reached) == _plain(os.path.abspath(target)) or same_path(link, target)


def manual_command(link, target):
    if WINDOWS:
        return f'mklink /J "{link}" "{target}"'
    return f'ln -s "{target}" "{link}"'


def make_link(link, target):
    link, target = Path(link), Path(target).resolve()
    link.parent.mkdir(parents=True, exist_ok=True)
    if not WINDOWS:
        os.symlink(target, link, target_is_directory=True)
        return
    done = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True,
                          text=True, errors="replace", timeout=TIMEOUT)
    if done.returncode != 0:
        raise OSError((done.stdout + done.stderr).strip() or "mklink failed")


def remove_link(link):
    if not is_link(link):
        raise OSError(f"{link} is not a link, left in place")
    if WINDOWS:
        os.rmdir(link)
    else:
        os.unlink(link)
