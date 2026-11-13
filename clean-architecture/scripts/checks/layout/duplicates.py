import hashlib
from collections import defaultdict

RULE = 1
MIN_CHARS = 32
SHOWN_DIGITS = 12


def fingerprint(item):
    if item["image"]:
        try:
            return hashlib.sha256(item["path"].read_bytes()).hexdigest()
        except OSError:
            return None
    body = "\n".join(line.rstrip() for line in item["lines"]).strip()
    return hashlib.sha256(body.encode()).hexdigest() if len(body) >= MIN_CHARS else None


def check(files, root, config):
    groups = defaultdict(list)
    for item in files:
        if not item["data"]:
            digest = fingerprint(item)
            if digest:
                groups[digest].append(item["rel"])
    findings = []
    for digest, paths in sorted(groups.items(), key=lambda pair: pair[1]):
        if len(paths) > 1:
            first, *others = sorted(paths)
            findings.append({"rule": RULE, "file": first, "line": 1, "what": f"same content as {', '.join(others)}",
                             "proof": f"sha256 {digest[:SHOWN_DIGITS]}"})
    return findings, {}
