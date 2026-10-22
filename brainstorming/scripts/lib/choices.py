from datetime import datetime

from common import read_json, write_json

NOTE_LIMIT = 4000
NOTHING = "nothing ticked"
EMPTY = "no choice yet"


def normalize(payload):
    screen = str(payload.get("screen", "")).strip() if isinstance(payload, dict) else ""
    selected = payload.get("selected") if screen else None
    if not screen or not isinstance(selected, dict):
        raise ValueError("a choice needs a screen name and a map of ticked values")
    picks = {str(name): [str(value) for value in values] for name, values in selected.items()
             if isinstance(values, list)}
    entry = {"selected": picks, "note": str(payload.get("note", ""))[:NOTE_LIMIT],
             "sent": bool(payload.get("sent")), "at": datetime.now().isoformat(timespec="seconds")}
    return screen, entry


def load(path):
    data = read_json(path) if path.exists() else None
    return data if isinstance(data, dict) else {}


def record(path, payload):
    screen, entry = normalize(payload)
    data = load(path)
    data[screen] = entry
    write_json(path, data)
    return screen, entry


def describe(screen, entry):
    state = "sent" if entry.get("sent") else "ticked, not sent yet"
    picks = "; ".join(f"{name} = {', '.join(values) or 'nothing'}"
                      for name, values in entry.get("selected", {}).items()) or NOTHING
    note = entry.get("note", "").strip()
    return f"{screen}: {state}, {picks}" + (f", note: {note}" if note else "")


def summary(data):
    return [describe(screen, entry) for screen, entry in data.items()] or [EMPTY]
