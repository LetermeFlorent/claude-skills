import hashlib
import json
import os
import time
from pathlib import Path

from store import store_dir

NOTES_NAME = "notes.json"
NOTES_VERSION = 1
FIRST_ID = 1
DATE_FORMAT = "%Y-%m-%d"
STALE_MARK = " stale"
JSON_INDENT = 1


def empty():
    return {"version": NOTES_VERSION, "next": FIRST_ID, "notes": []}


def load(root):
    try:
        data = json.loads((store_dir(root) / NOTES_NAME).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return empty()
    return data if data.get("version") == NOTES_VERSION else empty()


def save(root, data):
    folder = store_dir(root)
    folder.mkdir(parents=True, exist_ok=True)
    temp = folder / (NOTES_NAME + ".tmp")
    temp.write_text(json.dumps(data, indent=JSON_INDENT, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temp, folder / NOTES_NAME)


def add(data, text, hashes, about=None):
    number = data["next"]
    data["next"] = number + 1
    data["notes"].append({"id": number, "text": text, "about": list(about if about is not None else hashes),
                          "hashes": dict(hashes), "written": time.strftime(DATE_FORMAT)})
    return number


def drop(data, number):
    kept = [n for n in data["notes"] if n["id"] != number]
    found = len(kept) != len(data["notes"])
    data["notes"] = kept
    return found


def file_hash(root, path):
    try:
        return hashlib.sha256((Path(root) / path).read_bytes()).hexdigest()
    except OSError:
        return None


def is_stale(root, note):
    return any(file_hash(root, path) != digest for path, digest in note.get("hashes", {}).items())


def line(note, stale):
    about = f"  [about {', '.join(note['about'])}]" if note.get("about") else ""
    return f"note #{note['id']}{STALE_MARK if stale else ''}: {note['text']}{about}"
