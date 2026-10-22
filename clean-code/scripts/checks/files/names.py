import re
from pathlib import Path

from words import french

RULE = 15
SHOWN = 10
IDENTIFIER = re.compile(r"[A-Za-z_À-ɏ][\wÀ-ɏ]*")


def _path_names(rel):
    parts = Path(rel).parts
    return list(parts[:-1]) + [Path(rel).stem]


def _french_names(item):
    seen, first = [], 0
    for name in _path_names(item["rel"]):
        if french(name) and name not in seen:
            seen.append(name)
            first = first or 1
    for number, row in enumerate(item["rows"], 1):
        for identifier in IDENTIFIER.findall(row["code"]):
            if identifier not in seen and french(identifier):
                seen.append(identifier)
                first = first or number
    return seen, first


def check(files, root, config):
    findings, carrying, counted = [], 0, 0
    for item in files:
        if not item["code"] or item["data"]:
            continue
        counted += 1
        seen, first = _french_names(item)
        if not seen:
            continue
        carrying += 1
        more = f" and {len(seen) - SHOWN} more" if len(seen) > SHOWN else ""
        findings.append({"rule": RULE, "file": item["rel"], "line": first,
                         "what": f"{len(seen)} French identifiers: {', '.join(seen[:SHOWN])}{more}",
                         "proof": "names.py segment match"})
    return findings, {"files_with_french": carrying, "named_files": counted}
