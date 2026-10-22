import json
from pathlib import PurePosixPath

LIST_FIELDS = ("writes", "ports", "instances")
FLAG_FIELDS = ("commits", "heavy", "rebuild")


def clean_path(text):
    return PurePosixPath(str(text).replace("\\", "/").strip().rstrip("/")).as_posix().lower()


def normalize(raw, position):
    agent = {"name": str(raw.get("name") or f"agent-{position}"), "tree": clean_path(raw.get("tree") or ".")}
    for field in LIST_FIELDS:
        agent[field] = list(raw.get(field) or [])
    agent["writes"] = [clean_path(item) for item in agent["writes"]]
    agent["ports"] = [str(item) for item in agent["ports"]]
    agent["instances"] = [str(item).lower() for item in agent["instances"]]
    for field in FLAG_FIELDS:
        agent[field] = bool(raw.get(field))
    return agent


def load_plan(text):
    data = json.loads(text)
    items = data.get("agents") if isinstance(data, dict) else data
    if not isinstance(items, list) or not items:
        raise ValueError("the plan needs a non-empty list of agents")
    if not all(isinstance(item, dict) for item in items):
        raise ValueError("every agent must be an object")
    return [normalize(item, number) for number, item in enumerate(items, 1)]
