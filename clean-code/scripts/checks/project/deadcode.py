import re
from collections import Counter
from pathlib import PurePosixPath

from common import compact
from imports import commands, parse, public_files, resolve
from lexer import PYTHON_SUFFIX

RULE = 3
PACKAGE_INIT = "__init__.py"
CHECKED = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py"}
ENTRY_NAMES = {"index", "main", "app", "server", "cli", "__main__", "__init__", "setup", "conftest", "manage", "wsgi",
               "asgi", "middleware", "instrumentation", "page", "layout", "route", "loading", "error", "not-found",
               "template", "default", "worker", "vite-env", "global-error", "sitemap", "robots"}
ENTRY_DIRS = {"pages", "routes", "migrations", "scripts", "bin"}
MAIN = re.compile(r"__name__\s*==\s*['\"]__main__")
WORD = re.compile(r"[A-Za-z_$][\w$]*")
INTERPOLATION = re.compile(r"\{([^{}]+)\}")
CODE_LIKE = re.compile(r"^\s*\**\s*((const|let|var|function|return|import|export|if|for|while|def|class|await|async|"
                       r"from)\b|print\(|\w+(\.\w+)*\(.*\)\s*;?\s*$)|[;{}]\s*$|=>")
PY_SYMBOL = re.compile(r"^(?:async\s+def|def|class)\s+(\w+)")
ES_SYMBOL = re.compile(r"^(?:export\s+(?:default\s+)?(?:declare\s+)?(?:abstract\s+)?)?(?:async\s+)?"
                       r"(?:const|let|var|function\*?|class|interface|type|enum)\s+([A-Za-z_$][\w$]*)")


def _entry(item, public, scripts):
    rel = PurePosixPath(item["rel"])
    first = item["lines"][0] if item["lines"] else ""
    return (item["test"] or rel.name.split(".")[0] in ENTRY_NAMES or rel.name.startswith("+")
            or ".config." in rel.name or rel.name.endswith(".d.ts") or bool(set(rel.parts[:-1]) & ENTRY_DIRS)
            or item["rel"] in public or first.startswith("#!") or any(MAIN.search(line) for line in item["lines"])
            or any(item["rel"] in command or rel.name in command for command in scripts))


def _references(files, index):
    referenced, clauses = set(), {}
    for item in files:
        if not item["code"]:
            continue
        clauses[item["rel"]] = parse(item)
        for _, source, names in clauses[item["rel"]]:
            targets = [resolve(item, source, index)]
            if item["path"].suffix == PYTHON_SUFFIX:
                joiner = "" if source.endswith(".") else "."
                targets += [resolve(item, f"{source}{joiner}{imported}", index) for imported, _ in names]
            referenced.update(target for target in targets if target and target != item["rel"])
    return referenced, clauses


def _unused_imports(item, words, clauses):
    if PurePosixPath(item["rel"]).name == PACKAGE_INIT:
        return []
    return [(number, local) for number, _, names in clauses for _, local in names if words[local] <= 1]


def _commented_code(item):
    return [number for number, row in enumerate(item["rows"], 1)
            if row["comment"].strip() and not row["code"].strip() and not row["doc"]
            and CODE_LIKE.search(row["comment"])]


def _unused_symbols(item, words, everywhere):
    pattern = PY_SYMBOL if item["path"].suffix == PYTHON_SUFFIX else ES_SYMBOL
    found = []
    for number, row in enumerate(item["rows"], 1):
        match = pattern.match(row["code"])
        if match and not match.group(1).startswith("__") and everywhere[match.group(1)] - words[match.group(1)] == 0:
            if words[match.group(1)] <= 1 or row["code"].lstrip().startswith("export"):
                found.append((number, match.group(1)))
    return found


def _words(item):
    found = Counter()
    for row in item["rows"]:
        found.update(WORD.findall(row["code"]))
        found.update(word for text in row["strings"] for part in INTERPOLATION.findall(text)
                     for word in WORD.findall(part))
    return found


def _add(findings, item, pairs, what):
    if pairs:
        names = ", ".join(name for _, name in pairs if name)
        findings.append({"rule": RULE, "file": item["rel"], "line": pairs[0][0],
                         "what": f"{len(pairs)} {what}" + (f": {names}" if names else ""),
                         "proof": "lines " + compact(number for number, _ in pairs)})


def check(files, root, config):
    index = {item["rel"]: item for item in files}
    public, scripts = public_files(files, config), commands(files)
    referenced, clauses = _references(files, index)
    words = {item["rel"]: _words(item) for item in files}
    everywhere = sum(words.values(), Counter())
    findings, checked = [], 0
    for item in files:
        if not item["code"] or item["data"]:
            continue
        _add(findings, item, [(number, "") for number in _commented_code(item)], "commented-out code lines")
        if item["path"].suffix.lower() not in CHECKED:
            continue
        checked += 1
        entry = _entry(item, public, scripts)
        if item["rel"] not in referenced and not entry:
            findings.append({"rule": RULE, "file": item["rel"], "line": 1, "what": "file never imported",
                             "proof": "no import resolves to it and it is no entry point"})
        elif not entry or item["path"].suffix == PYTHON_SUFFIX:
            _add(findings, item, _unused_symbols(item, words[item["rel"]], everywhere), "symbols used nowhere")
        _add(findings, item, _unused_imports(item, words[item["rel"]], clauses.get(item["rel"], [])),
             "unused imports")
    return findings, {"dead_checked": checked, "referenced_files": len(referenced)}
