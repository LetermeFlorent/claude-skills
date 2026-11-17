import os
import shutil
import stat
import sys

from links import is_link, points_at, remove_link
from registry import file_hash

GIT_FOLDER = ".git"


def drop_link(label, link, target):
    if not os.path.lexists(link):
        return []
    if not is_link(link) or not points_at(link, target):
        return [(True, f"{label}: {link} is not ours, left as is")]
    try:
        remove_link(link)
    except OSError as error:
        return [(False, f"{label}: not removed ({error})")]
    return [(True, f"{label}: removed")]


def drop_file(label, path, recorded):
    if not path.is_file():
        return []
    if file_hash(path) != recorded:
        return [(True, f"{label}: changed by hand, left as is")]
    try:
        path.unlink()
    except OSError as error:
        return [(False, f"{label}: not removed ({error})")]
    return [(True, f"{label}: removed")]


def _force(function, path, _):
    os.chmod(path, stat.S_IWRITE)
    function(path)


def drop_checkout(label, folder):
    if not (folder / GIT_FOLDER).is_dir():
        return []
    handler = {"onexc": _force} if sys.version_info >= (3, 12) else {"onerror": _force}
    try:
        shutil.rmtree(folder, **handler)
    except OSError as error:
        return [(False, f"{label}: not removed ({error})")]
    return [(True, f"{label}: removed")]


def succeeded(lines):
    return all(ok for ok, _ in lines)
