import hashlib
import re
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath, PureWindowsPath

from common import DECODE_ERRORS, ENCODING
from parsers import HIGH, LEVELS, Raw, most_severe
from project import TEMPORARY

KEY_LENGTH = 10
SEVERE_CWES = frozenset({"22", "77", "78", "79", "89", "94", "502", "611", "798", "918"})
BLOCKING = frozenset(LEVELS[:LEVELS.index(HIGH) + 1])
NO_PATH = "-"
HISTORY_TOOL = "gitleaks-history"
ADVISORY = "advisory"
BUCKETS = SCOPE, ELSEWHERE, REVOKE, DISMISSED, IGNORED, TEMPORARY_FILES = (
    "scope", "elsewhere", "revoke", "dismissed", "ignored", "temporary")
OPEN, FIXED, NOT_APPLICABLE = "open", "fixed", "not-applicable"
ADVISORY_FORM = "<open|fixed|not-applicable> <level> <id> <path|-> : <note>"
ADVISORY_LINE = re.compile(r"^(open|fixed|not-applicable)\s+(\S+)\s+(\S+)\s+(\S+)\s*:\s*(.*)$", re.IGNORECASE)
ADVISORY_FIELDS = ("state", "level", "id", "path", "note")
MESSAGE_WIDTH, IDS_SHOWN = 100, 3


def relative_path(path, root):
    text = str(path or "").strip().replace("\\", "/")
    if not text or text == NO_PATH:
        return NO_PATH
    if text.startswith("/") or PureWindowsPath(text).drive:
        try:
            return Path(text).resolve().relative_to(root).as_posix()
        except (OSError, ValueError):
            return text
    return PurePosixPath(text).as_posix()


def source_line(root, path, line, cache):
    if line <= 0 or path == NO_PATH:
        return ""
    if path not in cache:
        try:
            cache[path] = (Path(root) / path).read_text(encoding=ENCODING, errors=DECODE_ERRORS).splitlines()
        except OSError:
            cache[path] = []
    return cache[path][line - 1].strip() if line <= len(cache[path]) else ""


def key_of(path, topic, anchor):
    return hashlib.sha256("\0".join((path, topic, anchor)).encode(ENCODING)).hexdigest()[:KEY_LENGTH]


def floor(level, topic):
    return HIGH if topic in SEVERE_CWES and LEVELS.index(level) > LEVELS.index(HIGH) else level


def merge(raws, root):
    groups, cache, seen, found = defaultdict(list), {}, Counter(), []
    for raw in raws:
        groups[(relative_path(raw.path, root), int(raw.line or 0), str(raw.topic or raw.ident))].append(raw)
    for (path, line, topic), group in sorted(groups.items()):
        ids = sorted({part for raw in group for part in str(raw.ident or "").split(",") if part})
        base = key_of(path, topic, source_line(root, path, line, cache) or ",".join(ids))
        seen[base] += 1
        found.append({"key": base if seen[base] == 1 else f"{base}#{seen[base]}", "path": path, "line": line,
                      "level": floor(most_severe([raw.level for raw in group]), topic), "topic": topic,
                      "tools": sorted({raw.tool for raw in group}), "ids": ids, "message": group[0].message})
    return sorted(found, key=lambda item: (LEVELS.index(item["level"]), item["path"], item["line"], item["key"]))


def merge_all(raws, root):
    history = merge([raw for raw in raws if raw.tool == HISTORY_TOOL], root)
    return merge([raw for raw in raws if raw.tool != HISTORY_TOOL], root) + [{**item, "history": True}
                                                                             for item in history]


def false_positives(lines):
    accepted, bad = {}, []
    for line in lines:
        key, _, reason = line.partition(" ")
        if reason.strip():
            accepted[key] = reason.strip()
        else:
            bad.append(f"{line}: no reason after the key")
    return accepted, bad


def advisory_problem(match, names):
    if not match:
        return f"not {ADVISORY_FORM}"
    state, level, _, path, note = match.groups()
    if level.lower() not in LEVELS:
        return f"level {level} is not one of {', '.join(LEVELS)}"
    if path != NO_PATH and path not in names:
        return f"{path} is not a file of the project"
    if state.lower() == NOT_APPLICABLE and not note.strip():
        return "not-applicable needs its reason after the colon"
    return None


def advisories(lines, names):
    entries, bad = [], []
    for line in lines:
        match = ADVISORY_LINE.match(line)
        problem = advisory_problem(match, names)
        if problem:
            bad.append(f"{line}: {problem}")
            continue
        entry = dict(zip(ADVISORY_FIELDS, match.groups()))
        entries.append({**entry, "state": entry["state"].lower(), "level": entry["level"].lower()})
    return entries, bad


def advisory_raws(entries):
    return [Raw(ADVISORY, entry["id"], entry["level"], entry["path"], 0, entry["note"], f"{ADVISORY}:{entry['id']}")
            for entry in entries if entry["state"] == OPEN]


def bucket(finding, scope, names, dismissed):
    path = finding["path"]
    if TEMPORARY.search(path):
        return TEMPORARY_FILES
    if finding["key"] in dismissed:
        return DISMISSED
    if finding.get("history"):
        return REVOKE
    if path != NO_PATH and path not in names:
        return IGNORED
    return SCOPE if path in scope else ELSEWHERE


def split(findings, scope, names, dismissed):
    buckets = {name: [] for name in BUCKETS}
    for finding in findings:
        buckets[bucket(finding, scope, names, dismissed)].append(finding)
    return buckets


def blocking(findings):
    return [finding for finding in findings if finding["level"] in BLOCKING]


def row(finding):
    where = f"{finding['path']}:{finding['line']}" if finding["line"] else finding["path"]
    ids, hidden = finding["ids"][:IDS_SHOWN], len(finding["ids"]) - IDS_SHOWN
    ids += [f"+{hidden}"] if hidden > 0 else []
    message = " ".join(str(finding["message"]).split())[:MESSAGE_WIDTH]
    return f"{finding['level']} {finding['key']} {where} {','.join(finding['tools'])} {','.join(ids)}: {message}"
