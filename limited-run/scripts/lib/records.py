import json
import os
import re
import tempfile
import time
from pathlib import Path

import procs

ENV = "LIMITED_RUN_STATE"
SUFFIX = ".json"
ENCODING = "utf-8"
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,39}$")
NOT_WORD = re.compile(r"[^a-z0-9]+")
BASE_LENGTH = 24
MAX_COUNTER = 999
UNREADABLE_GRACE_SECONDS = 60
REPLACE_TRIES, REPLACE_PAUSE = 20, 0.05


def state_dir():
    folder = Path(os.environ.get(ENV) or Path(tempfile.gettempdir()) / "limited-run")
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def valid_name(name):
    return bool(NAME.match(name or ""))


def base_name(command):
    stem = NOT_WORD.sub("-", Path(command[0]).stem.lower()).strip("-") if command else ""
    return (stem or "task")[:BASE_LENGTH].rstrip("-")


def read(path):
    try:
        return json.loads(path.read_text(encoding=ENCODING))
    except (OSError, ValueError):
        return None


def is_live(record):
    return isinstance(record, dict) and procs.same(record.get("launcher_pid"), record.get("launcher_created"))


def _replace(source, target):
    for attempt in range(REPLACE_TRIES):
        try:
            os.replace(source, target)
            return
        except PermissionError:
            if attempt == REPLACE_TRIES - 1:
                raise
            time.sleep(REPLACE_PAUSE)


def _publish(path, record, exclusive):
    temp = path.with_name(f".{path.stem}.{os.getpid()}.tmp")
    temp.write_text(json.dumps(record), encoding=ENCODING)
    try:
        if exclusive:
            os.link(temp, path)
        else:
            _replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def claim(folder, name, record):
    path = folder / f"{name}{SUFFIX}"
    for _ in range(REPLACE_TRIES):
        try:
            _publish(path, {**record, "name": name}, exclusive=True)
            return True
        except FileExistsError:
            existing = read(path)
            if is_live(existing) or existing is None and path.exists():
                return False
            path.unlink(missing_ok=True)
    return False


def claim_next(folder, command, record):
    base = base_name(command)
    for counter in range(1, MAX_COUNTER + 1):
        if claim(folder, f"{base}-{counter}", record):
            return f"{base}-{counter}"
    return None


def update(folder, name, fields):
    path = folder / f"{name}{SUFFIX}"
    _publish(path, {**(read(path) or {}), **fields}, exclusive=False)


def release(folder, name, launcher_pid):
    path = folder / f"{name}{SUFFIX}"
    record = read(path)
    if record is not None and record.get("launcher_pid") == launcher_pid:
        path.unlink(missing_ok=True)


def forget(folder, name):
    (folder / f"{name}{SUFFIX}").unlink(missing_ok=True)


def _stale(path):
    try:
        return time.time() - path.stat().st_mtime > UNREADABLE_GRACE_SECONDS
    except OSError:
        return False


def live_records(folder):
    found = []
    for path in sorted(folder.glob(f"*{SUFFIX}")):
        record = read(path)
        if record is None:
            if _stale(path):
                path.unlink(missing_ok=True)
        elif is_live(record):
            found.append(record)
        else:
            path.unlink(missing_ok=True)
    return sorted(found, key=lambda item: item.get("started", 0))
