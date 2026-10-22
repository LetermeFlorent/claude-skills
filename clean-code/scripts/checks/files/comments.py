import re

from common import compact
from imports import public_files
from lexer import is_directive

RULE = 14
LICENCE = re.compile(r"licen[cs]e|copyright|spdx", re.IGNORECASE)


def _header(rows):
    lines, text = set(), ""
    for number, row in enumerate(rows, 1):
        if row["code"].strip():
            break
        lines.add(number)
        text += row["comment"]
    return lines if LICENCE.search(text) else set()


def check(files, root, config):
    public = public_files(files, config)
    findings, counted, carrying = [], 0, 0
    for item in files:
        if not item["code"] or item["data"]:
            continue
        counted += 1
        rows, header, hits = item["rows"], _header(item["rows"]), []
        for number, row in enumerate(rows, 1):
            if not row["comment"]:
                continue
            if number in header or (number == 1 and item["lines"][0].startswith("#!")):
                continue
            if is_directive(row["comment"]):
                continue
            if row["doc"] and item["rel"] in public:
                continue
            hits.append(number)
        if hits:
            carrying += 1
            findings.append({"rule": RULE, "file": item["rel"], "line": hits[0],
                             "what": f"{len(hits)} comment lines", "proof": "lines " + compact(hits)})
    stats = {"comment_scanned": counted, "files_with_comments": carrying, "public_api": sorted(public)}
    return findings, stats
