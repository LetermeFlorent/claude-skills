import json
import re
from pathlib import PurePosixPath

from lexer import PYTHON_SUFFIX

FUTURE = "__future__"
SOURCE, SOURCE_DIR = "src", "src"
MANIFEST = "package.json"
ES_SUFFIXES = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte", ".json", ".d.ts")
ES_FROM = re.compile(r"^\s*(?:import|export)\s+(?:type\s+)?(?P<what>[^'\"]*?)\s*from\s*['\"](?P<src>[^'\"]+)['\"]")
ES_BARE = re.compile(r"^\s*import\s*['\"](?P<src>[^'\"]+)['\"]")
ES_CALL = re.compile(r"\b(?:require|import)\(\s*['\"](?P<src>[^'\"]+)['\"]\s*\)")
PY_IMPORT = re.compile(r"^\s*import\s+(?P<what>[\w., ]+)$")
PY_FROM = re.compile(r"^\s*from\s+(?P<src>[\w.]+)\s+import\s+(?P<what>.+)$")
ALIASES = {"@/": "src/", "~/": "src/"}
MULTILINE = re.compile(r"^\s*(import|from)\b.*[{(]\s*$|^\s*export\s+(type\s+)?\{\s*$")
PUBLIC_KEYS = ("exports", "main", "module", "types", "typings")
COMMAND_KEYS = ("scripts", "bin")


def _clauses(item):
    pending, start = "", 0
    for number, line in enumerate(item["lines"], 1):
        if not item["rows"][number - 1]["code"].strip() and not pending:
            continue
        if pending or MULTILINE.match(line):
            pending, start = (pending + " " + line.strip()) if pending else line.strip(), start or number
            if not re.search(r"[})]", line):
                continue
            yield start, pending
            pending, start = "", 0
            continue
        yield number, line


def _names(what):
    names = []
    for piece in re.split(r",", what.replace("{", ",").replace("}", ",").replace("(", "").replace(")", "")):
        piece = re.sub(r"^\s*type\s+", "", piece).strip()
        if not piece or piece == "*":
            continue
        local = piece.split(" as ")[-1].strip()
        names.append((piece.split(" as ")[0].strip(), local.split(".")[0] if " as " not in piece else local))
    return names


def parse(item):
    found, python = [], item["path"].suffix == PYTHON_SUFFIX
    for number, line in _clauses(item):
        if python:
            match = PY_FROM.match(line) or PY_IMPORT.match(line)
            if match and SOURCE in match.groupdict() and match.group(SOURCE) != FUTURE:
                found.append((number, match.group(SOURCE), _names(match.group("what"))))
            elif match and SOURCE not in match.groupdict():
                found.extend((number, imported, [(imported, local)]) for imported, local in _names(match.group("what")))
            continue
        match = ES_FROM.match(line) or ES_BARE.match(line)
        if match:
            what = match.groupdict().get("what") or ""
            names = [] if line.lstrip().startswith("export") else _names(what)
            found.append((number, match.group(SOURCE), names))
        found.extend((number, call.group(SOURCE), []) for call in ES_CALL.finditer(line))
    return found


def _first(candidates, index):
    return next((candidate for candidate in candidates if candidate in index), None)


def resolve(item, source, index):
    base = PurePosixPath(item["rel"]).parent
    if item["path"].suffix == PYTHON_SUFFIX:
        dots = len(source) - len(source.lstrip("."))
        module = source.lstrip(".").replace(".", "/")
        plain = [PurePosixPath(""), PurePosixPath(SOURCE_DIR), base]
        roots = [base.joinpath(*[".."] * max(0, dots - 1))] if dots else plain
        for folder in roots:
            target = _normal(folder / module) if module else _normal(folder)
            found = _first([f"{target}.py", f"{target}/__init__.py"], index)
            if found:
                return found
        return None
    for alias, prefix in ALIASES.items():
        if source.startswith(alias):
            source, base = prefix + source[len(alias):], PurePosixPath("")
    if not source.startswith((".", "src/")):
        return None
    target = _normal(base / source) if source.startswith(".") else source
    stem = re.sub(r"\.(m|c)?js$", "", target)
    candidates = [target] + [stem + suffix for suffix in ES_SUFFIXES] + [f"{target}/index{suffix}" for suffix in
                                                                         ES_SUFFIXES]
    return _first(candidates, index)


def _normal(path):
    parts = []
    for part in PurePosixPath(path).parts:
        if part == "..":
            parts = parts[:-1]
        elif part != ".":
            parts.append(part)
    return "/".join(parts)


def _targets(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for inner in value.values():
            yield from _targets(inner)
    elif isinstance(value, list):
        for inner in value:
            yield from _targets(inner)


def _manifests(files):
    for item in files:
        if PurePosixPath(item["rel"]).name != MANIFEST:
            continue
        try:
            yield PurePosixPath(item["rel"]).parent, json.loads("\n".join(item["lines"]))
        except ValueError:
            continue


def public_files(files, config):
    public = {_normal(base / target) for base, manifest in _manifests(files) for key in PUBLIC_KEYS
              for target in _targets(manifest.get(key))}
    patterns = [pattern.rstrip("/") for pattern in config.get("public_api", [])]
    public.update(item["rel"] for item in files
                  if any(item["rel"] == pattern or item["rel"].startswith(pattern + "/") for pattern in patterns))
    return public


def commands(files):
    return [str(target) for _, manifest in _manifests(files) for key in COMMAND_KEYS
            for target in _targets(manifest.get(key))]
