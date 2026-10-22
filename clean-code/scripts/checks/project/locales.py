import json
import re
from collections import defaultdict
from pathlib import PurePosixPath

from common import compact
from files import LANG_CODE
from words import french, french_text

TEXT_RULE = 17
PROPERTIES = ".properties"
NAME_RULE = 15
UI_SUFFIXES = {".tsx", ".jsx", ".vue", ".svelte", ".html"}
UI_DIRS = {"ui", "components", "pages", "views", "screens", "app", "templates", "widgets", "layouts"}
TEXT_NODE = re.compile(r">([^<>{}]*[^\W\d_]{2,}[^<>{}]*)<")
SENTENCE_WORDS = 3
SHOWN = 8


def _flatten(value, prefix=""):
    if isinstance(value, dict):
        for key, inner in value.items():
            yield from _flatten(inner, f"{prefix}{key}.")
    else:
        yield prefix[:-1]


def _keys(item):
    suffix = item["path"].suffix.lower()
    if suffix in (".json", ".arb"):
        try:
            return {key for key in _flatten(json.loads("\n".join(item["lines"]))) if not key.startswith("@")}
        except ValueError:
            return None
    if suffix == PROPERTIES:
        return {line.split("=", 1)[0].strip() for line in item["lines"]
                if "=" in line and not line.lstrip().startswith(("#", "!"))}
    return None


def _language(rel):
    path = PurePosixPath(rel)
    if LANG_CODE.match(path.stem):
        return path.stem, f"{path.parent}/*{path.suffix}"
    for index, part in enumerate(path.parts[:-1]):
        if LANG_CODE.match(part):
            return part, "/".join(path.parts[:index] + ("*",) + path.parts[index + 1:])
    return None, None


def _gaps(locales):
    groups = defaultdict(dict)
    for item in locales:
        language, group = _language(item["rel"])
        keys = _keys(item)
        if language and keys is not None:
            groups[group][item["rel"]] = keys
    for members in groups.values():
        every = set().union(*members.values()) if len(members) > 1 else set()
        for rel, keys in members.items():
            missing = sorted(every - keys)
            if missing:
                yield rel, missing, sorted(set(members) - {rel})


def _visible(item):
    ui = item["path"].suffix.lower() in UI_SUFFIXES or bool(set(PurePosixPath(item["rel"]).parts[:-1]) & UI_DIRS)
    hits = []
    for number, row in enumerate(item["rows"], 1):
        texts = row["strings"] + (TEXT_NODE.findall(row["code"]) if ui else [])
        if any(french_text(text) or (ui and len(text.split()) >= SENTENCE_WORDS) for text in texts):
            hits.append(number)
    return hits


def _outside(files):
    findings = []
    for item in files:
        hits = _visible(item) if item["code"] and not item["test"] and not item["data"] else []
        if hits:
            findings.append({"rule": TEXT_RULE, "file": item["rel"], "line": hits[0],
                             "what": f"{len(hits)} lines with user-visible text outside the translations",
                             "proof": "lines " + compact(hits)})
    return findings


def check(files, root, config):
    locales = [item for item in files if item["locale"]]
    findings = []
    for rel, missing, others in _gaps(locales):
        findings.append({"rule": TEXT_RULE, "file": rel, "line": 1,
                         "what": f"{len(missing)} keys missing: " + ", ".join(missing[:SHOWN]),
                         "proof": "compared with " + ", ".join(others)})
    for item in locales:
        named = sorted({key for key in (_keys(item) or ()) if any(french(part) for part in key.split("."))})
        if named:
            findings.append({"rule": NAME_RULE, "file": item["rel"], "line": 1,
                             "what": f"{len(named)} French translation keys: " + ", ".join(named[:SHOWN]),
                             "proof": "words.py segment match"})
    findings += _outside(files) if locales else []
    return findings, {"has_locales": bool(locales), "locale_files": len(locales)}
