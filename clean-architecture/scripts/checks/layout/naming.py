import re
from collections import defaultdict
from pathlib import PurePosixPath

from files import TEST_DIRS

NAMING_RULE = 7
TESTS_RULE = 8
STYLES = (("snake_case", re.compile(r"^[a-z0-9]+(_[a-z0-9]+)+$")),
          ("kebab-case", re.compile(r"^[a-z0-9]+(-[a-z0-9]+)+$")),
          ("camelCase", re.compile(r"^[a-z][a-z0-9]*([A-Z][a-z0-9]*)+$")),
          ("PascalCase", re.compile(r"^([A-Z][a-z0-9]+)+$")))
FREE_STEMS = {"index", "main", "__init__", "__main__", "readme", "conftest"}
SHOWN = 3
PLACES = ("in a test folder", "next to the code")


def style(stem):
    return next((name for name, pattern in STYLES if pattern.match(stem)), None)


def mixed_names(files):
    styles = defaultdict(lambda: defaultdict(list))
    for item in files:
        path = PurePosixPath(item["rel"])
        stem = path.name.split(".")[0]
        kind = style(stem) if item["code"] and stem.lower() not in FREE_STEMS else None
        if kind:
            styles[str(path.parent)][kind].append(path.name)
    findings = []
    for folder, kinds in sorted(styles.items()):
        if len(kinds) > 1:
            parts = [f"{kind}: {', '.join(sorted(names)[:SHOWN])}" for kind, names in sorted(kinds.items())]
            findings.append({"rule": NAMING_RULE, "file": folder, "line": 0,
                             "what": f"{len(kinds)} file naming styles in one folder", "proof": "; ".join(parts)})
    return findings


def test_places(files):
    places = defaultdict(list)
    for item in files:
        if item["test"] and any(line.strip() for line in item["lines"]):
            inside = bool({part.lower() for part in PurePosixPath(item["rel"]).parts[:-1]} & TEST_DIRS)
            places[PLACES[0] if inside else PLACES[1]].append(item["rel"])
    if len(places) < len(PLACES):
        return []
    fewer, more = sorted(places, key=lambda place: (len(places[place]), place))
    return [{"rule": TESTS_RULE, "file": rel, "line": 0, "what": f"test {fewer}, {len(places[more])} other {more}",
             "proof": f"{more}: {len(places[more])}, {fewer}: {len(places[fewer])}"} for rel in places[fewer]]


def check(files, root, config):
    return mixed_names(files) + test_places(files), {}
