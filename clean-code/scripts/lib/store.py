import os
import time
from contextlib import contextmanager, suppress

from common import read_json, write_json
from runs import FINDINGS

CANDIDATE, CONFIRMED, REFUTED = "candidate", "confirmed", "refuted"
CAPS = ("secret", "build", "swallowed", "test-in-prod", "attribution")
SECRET, BUILD, SWALLOWED, TEST_IN_PROD, ATTRIBUTION = CAPS
NO_CAP = "none"
LOCK = "findings.lock"
SCRATCH = "findings.tmp"
LISTS = ("unmeasured", "checked")
LOCK_WAIT = 20
LOCK_STALE = 60
POLL = 0.1


def _taken(lock):
    try:
        os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError:
        return False
    return True


def _acquire(lock):
    deadline = time.monotonic() + LOCK_WAIT
    while not _taken(lock):
        with suppress(FileNotFoundError):
            if time.time() - lock.stat().st_mtime > LOCK_STALE:
                lock.unlink()
        if time.monotonic() > deadline:
            raise TimeoutError(f"{lock} held for {LOCK_WAIT} s by another writer")
        time.sleep(POLL)


@contextmanager
def opened(run, save=True):
    path, lock = run / FINDINGS, run / LOCK
    _acquire(lock)
    try:
        payload = read_json(path)
        for key in LISTS:
            payload.setdefault(key, [])
        yield payload
        if save:
            write_json(run / SCRATCH, payload)
            os.replace(run / SCRATCH, path)
    finally:
        lock.unlink(missing_ok=True)
