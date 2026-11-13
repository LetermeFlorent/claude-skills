"""Projects on the board, kept in .state.json and pushed to every open page. cfg is in seconds and set from the page:
window is the time the chart width shows, done the delay before a finished project leaves, idle the delay before a
project with no report leaves and its color and icon are forgotten."""
import json
import queue
import random
import threading
import time
from pathlib import Path
from urllib.parse import parse_qs, unquote

HERE = Path(__file__).resolve().parent.parent
PAGE = HERE / "site" / "index.html"
STATE = HERE / ".state.json"
ICONS = ["star", "bolt", "heart", "moon", "diamond", "flame", "crown", "leaf"]
COLORS, DONE, MAX_POINTS, SWEEP_EVERY = 8, 100, 500, 30
HOUR, DAY = 3600, 86400
DEFAULTS = {"window": HOUR, "done": HOUR, "idle": 3 * DAY}
LIMITS = {"window": (60, DAY), "done": (60, 7 * DAY), "idle": (HOUR, 60 * DAY)}

lock = threading.Lock()
listeners: list[queue.Queue] = []


def load() -> dict:
    try:
        data = json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    cfg = {**DEFAULTS, **data.get("cfg", {})}
    return {"projects": data.get("projects", []), "known": data.get("known", {}), "cfg": cfg}


state = load()


def save() -> None:
    temp, text = STATE.with_name(STATE.name + ".tmp"), json.dumps(state, ensure_ascii=False)
    temp.write_text(text, encoding="utf-8")
    for _ in range(20):
        try:
            return temp.replace(STATE)
        except PermissionError:
            time.sleep(0.05)
    STATE.write_text(text, encoding="utf-8")
    temp.unlink(missing_ok=True)


def page() -> str:
    """The full state; v, the page file's date, lets an open tab notice a new page and reload once."""
    full = {"projects": state["projects"], "cfg": state["cfg"], "v": int(PAGE.stat().st_mtime)}
    return json.dumps(full, ensure_ascii=False)


def push(data: str) -> None:
    for q in listeners:
        q.put(data)


def prune(now: float) -> bool:
    cfg = state["cfg"]

    def stays(p: dict) -> bool:
        last = p["history"][-1]
        return now - last["ts"] < (cfg["done"] if last["v"] >= DONE else cfg["idle"])

    state["known"] = {k: v for k, v in state["known"].items() if len(v) > 3 and now - v[3] < cfg["idle"]}
    before = len(state["projects"])
    state["projects"] = [p for p in state["projects"] if stays(p)]
    return len(state["projects"]) != before


def new_project(name: str) -> dict:
    """A returning name gets its old color and icon back, unless a project on screen wears that pair.
    Otherwise an icon nobody shows, or past eight projects one no other project of that color shows."""
    shown = {(p["slot"] % COLORS, p["icon"]) for p in state["projects"]}
    old = state["known"].get(name)
    if old and (old[0] % COLORS, old[1]) not in shown:
        return {"name": name, "slot": old[0], "icon": old[1], "history": []}
    used = {p["slot"] for p in state["projects"]}
    slot = next(i for i in range(len(used) + 1) if i not in used)
    free = [i for i in ICONS if i not in {p["icon"] for p in state["projects"]}]
    free = free or [i for i in ICONS if (slot % COLORS, i) not in shown] or ICONS
    return {"name": name, "slot": slot, "icon": random.choice(free), "history": []}


def find(name: str, pct: int) -> dict | None:
    """None drops the report: a late 100 from a finished project that left, or a second 100 in a row."""
    proj = next((p for p in state["projects"] if p["name"] == name), None)
    if proj is None:
        if pct >= DONE and state["known"].get(name, [0, 0, False])[2]:
            return None
        proj = new_project(name)
        state["projects"].append(proj)
    elif pct >= DONE and proj["history"] and proj["history"][-1]["v"] >= DONE:
        return None
    return proj


def add_point(proj: dict, pct: int, step: str, now: float) -> None:
    """Every line starts at 0 %, never goes back in time, and keeps its start when trimmed."""
    hist = proj["history"]
    ts = int(max(now, hist[-1]["ts"])) if hist else int(now)
    start = [] if hist or pct == 0 else [{"ts": ts, "v": 0, "s": ""}]
    hist = hist + start + [{"ts": ts, "v": pct, "s": step}]
    proj["history"] = hist if len(hist) <= MAX_POINTS else hist[:1] + hist[-(MAX_POINTS - 1):]
    proj["step"] = step or proj.get("step", "")
    state["known"][proj["name"]] = [proj["slot"], proj["icon"], pct >= DONE, ts]


def update(name: str, pct: int, step: str, now: float) -> None:
    with lock:
        pruned = prune(now)
        proj = find(name, pct)
        if proj is None:
            return
        add_point(proj, pct, step, now)
        save()
        push(page() if pruned else json.dumps({"p": proj}, ensure_ascii=False))


def admin(path: str, query: str) -> bool:
    """Settings from the page: /_cfg?window=&done=&idle=, /_del/<project>, /_clear. False for another path."""
    with lock:
        if path == "/_cfg":
            for k, v in parse_qs(query).items():
                if k in LIMITS and v[0].isdigit():
                    state["cfg"][k] = max(LIMITS[k][0], min(LIMITS[k][1], int(v[0])))
        elif path.startswith("/_del/"):
            name = unquote(path[len("/_del/"):])
            state["projects"] = [p for p in state["projects"] if p["name"] != name]
            state["known"].pop(name, None)
        elif path == "/_clear":
            state["projects"], state["known"] = [], {}
        else:
            return False
        prune(time.time())
        save()
        push(page())
    return True


def sweep() -> None:
    """Removes expired projects even when no agent reports anything."""
    while True:
        time.sleep(SWEEP_EVERY)
        with lock:
            if prune(time.time()):
                save()
                push(page())
