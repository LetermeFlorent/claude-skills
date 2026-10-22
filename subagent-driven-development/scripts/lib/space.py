import hashlib
import re
import tempfile
from pathlib import Path

from common import DECODE_ERRORS, ENCODING, read_json, short, write_json
from repo import in_tree

TEMP_PARTS = ("claude-skills",)
SUFFIX = "-sdd"
LEDGER = "progress.md"
HASH_LENGTH = 6
IGNORED = ".ia/"
TOOLING = (".ia/", ".git/")
TASK_ID = re.compile(r"^(\d+(?:,\d+)*|final)$")
UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


def temp_root():
    return Path(tempfile.gettempdir()).joinpath(*TEMP_PARTS)


def folder_for(base, project, plan):
    digest = hashlib.sha1(plan.as_posix().lower().encode(ENCODING)).hexdigest()[:HASH_LENGTH]
    name = UNSAFE.sub("-", plan.stem).strip("-") or "plan"
    return base / f"{project}{SUFFIX}" / f"{name}-{digest}"


def stem(task_id):
    if not TASK_ID.match(task_id):
        raise ValueError(f"task id {task_id!r}: a number, numbers joined by commas, or final")
    return "task-" + task_id.replace(",", "+")


def named(folder, task_id, tail):
    return folder / f"{stem(task_id)}{tail}"


def record_path(folder, task_id):
    return named(folder, task_id, ".json")


def load_record(folder, task_id):
    path = record_path(folder, task_id)
    return read_json(path) if path.exists() else None


def save_record(folder, task_id, record):
    write_json(record_path(folder, task_id), record)


def package_path(folder, task_id, left, right):
    return named(folder, task_id, f"-{short(left)}..{short(right)}.diff")


def review_path(folder, task_id, right):
    return named(folder, task_id, f"-{short(right)}-review.md")


def gate_path(folder, task_id, right):
    return named(folder, task_id, f"-{short(right)}-gate.txt")


def ensure_excluded(exclude):
    text = exclude.read_text(encoding=ENCODING, errors=DECODE_ERRORS) if exclude.exists() else ""
    if IGNORED in text.split():
        return False
    exclude.parent.mkdir(parents=True, exist_ok=True)
    joiner = "" if text.endswith("\n") or not text else "\n"
    exclude.write_text(text + joiner + IGNORED + "\n", encoding=ENCODING)
    return True


def _problem(root, raw, full):
    try:
        rel = full.relative_to(root).as_posix()
    except ValueError:
        return None, f"{raw} is outside the repository {root.as_posix()}"
    if any(rel == part.rstrip("/") or rel.startswith(part) for part in TOOLING):
        return None, f"{rel} is tooling, never part of a task"
    if full.is_dir():
        return None, f"{rel} is a folder: name its files one by one"
    return rel, None


def claimed(root, raws):
    paths, problems = [], []
    for raw in raws:
        given = Path(raw)
        rel, problem = _problem(root, raw, (given if given.is_absolute() else root / given).resolve())
        if problem:
            problems.append(problem)
        else:
            paths.append(rel)
    return list(dict.fromkeys(paths)), problems


def task_paths(record, root, raws):
    paths, problems = claimed(root, raws)
    problems += [f"{path} does not exist and is not in the base commit" for path in paths
                 if not (root / path).exists() and not in_tree(root, record["base"], path)]
    earlier = [path for snap in record["snapshots"] for path in snap["paths"]]
    return list(dict.fromkeys(earlier + paths)), paths, problems
