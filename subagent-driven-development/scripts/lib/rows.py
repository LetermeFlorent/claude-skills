import codecs
import re
from pathlib import PurePosixPath

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
SCAN_ROW = re.compile(r"^(?P<file>.+?)(?::(?P<line>\d+))? (?P<status>fixed|by hand|flag): (?P<kind>.+)$")
GROUPED = re.compile(r" \(lines (?P<lines>[\d, ]+)(?P<more> \(\+\d+\))?\)$")
KIND = r"(?:[a-z]+(?: [a-z]+)*|repeated (?:'[^']*'|" + '"[^"]*"))'
SEGMENT = KIND + r" (\d+(?:-\d+)?(?:, \d+(?:-\d+)?)*)"
SPANS = re.compile(rf"^{SEGMENT}(?:; {SEGMENT})*$")
SEGMENTS = re.compile(SEGMENT)
SPAN = re.compile(r"(\d+)(?:-(\d+))?")
DIFF_START, NEW_MODE, OLD_SIDE, NEW_SIDE, NO_FILE = "diff --git ", "new file mode", "--- ", "+++ ", "/dev/null"
OLD_PREFIX, NEW_PREFIX = "a/", "b/"
TAB = chr(9)
CLEAN_CODE, ANTI_EMPREINTE = "clean-code", "anti-empreinte"


def _unquote(value):
    value = value.rstrip(TAB)
    if len(value) > 1 and value[0] == value[-1] == '"':
        return codecs.escape_decode(value[1:-1].encode("latin-1", "backslashreplace"))[0].decode("utf-8", "replace")
    return value


def _header(line, state, files):
    if line.startswith(NEW_MODE) or line == OLD_SIDE + NO_FILE:
        state["new"] = True
    elif line.startswith(OLD_SIDE):
        state["old"] = _unquote(line[len(OLD_SIDE):]).removeprefix(OLD_PREFIX)
    elif line.startswith(NEW_SIDE):
        target = _unquote(line[len(NEW_SIDE):])
        state["header"] = False
        state["path"] = None if target == NO_FILE else target.removeprefix(NEW_PREFIX)
        if state["path"]:
            files[state["path"]] = {"new": state["new"], "deleted": False, "lines": set()}
        elif state["old"]:
            files[state["old"]] = {"new": False, "deleted": True, "lines": set()}


def changed_lines(text):
    files, state = {}, {"header": False, "path": None, "old": None, "new": False}
    for line in text.splitlines():
        if line.startswith(DIFF_START):
            state.update(header=True, path=None, old=None, new=False)
        elif state["header"]:
            _header(line, state, files)
        elif state["path"]:
            match = HUNK.match(line)
            if match:
                start, count = int(match.group(1)), int(match.group(2) or 1)
                files[state["path"]]["lines"].update(range(start, start + count))
    return files


def _child(folder, path):
    return PurePosixPath(path).parent.as_posix() == folder.rstrip("/")


def counts(row, changes):
    change = changes.get(row["file"])
    if change is None:
        return any(item["new"] and _child(row["file"], path) for path, item in changes.items())
    if change["new"] or row.get("truncated"):
        return True
    if row["exact"]:
        return any(line in change["lines"] for line in row["lines"])
    return bool(change["lines"])


def proof_lines(proof):
    if not SPANS.match(proof or ""):
        return []
    found = []
    for segment in SEGMENTS.finditer(proof):
        for first, last in SPAN.findall(segment.group(1)):
            found.extend(range(int(first), int(last or first) + 1))
    return found


def _measure_row(item):
    line = int(item.get("line") or 0)
    lines = proof_lines(item.get("proof")) or ([line] if line > 1 else [])
    return {"source": CLEAN_CODE, "file": item["file"], "lines": lines, "exact": bool(lines),
            "text": f"rule {item['rule']}: {item['what']} | {item['proof']}"}


def from_measure(findings):
    return [_measure_row(item) for item in findings]


def _scan_row(line):
    match = SCAN_ROW.match(line.strip())
    if not match:
        return None
    kind, lines = match.group("kind"), [int(match.group("line"))] if match.group("line") else []
    grouped = GROUPED.search(kind)
    if grouped:
        lines = [int(part) for part in grouped.group("lines").replace(" ", "").split(",") if part]
    return {"source": ANTI_EMPREINTE, "file": match.group("file"), "lines": lines, "exact": bool(lines),
            "truncated": bool(grouped and grouped.group("more")),
            "text": f"{match.group('status')}: {kind}"}


def from_scan(output):
    return [row for row in map(_scan_row, output.splitlines()) if row]


def split(rows, changes):
    counted = [row for row in rows if counts(row, changes)]
    return counted, [row for row in rows if row["file"] in changes and row not in counted]


def show(row):
    where = row["file"] + (f":{row['lines'][0]}" if row["lines"] and row["lines"][0] else "")
    return f"{row['source']} | {where} | {row['text']}"
