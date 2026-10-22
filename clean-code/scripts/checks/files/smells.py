import re

from common import compact
from lexer import PYTHON_SUFFIX, is_directive
from store import SWALLOWED, TEST_IN_PROD

LOOSE_TYPE = re.compile(r":\s*any\b|\bas\s+any\b|<any>|\bany\[\]|@ts-ignore|@ts-nocheck|type:\s*ignore|#\s*noqa\b")
EMPTY_CATCH = re.compile(r"\bcatch\b\s*(\([^)]*\))?\s*\{\s*\}")
OPEN_CATCH = re.compile(r"\bcatch\b\s*(\([^)]*\))?\s*\{\s*$")
EXCEPT = re.compile(r"^\s*except\b[^:]*:")
BROAD = re.compile(r"^\s*except\s*(\(?\s*(Exception|BaseException)\b[^:]*)?:")
QUIET = re.compile(r"^\s*(pass|\.\.\.)\s*$")
SILENT_BODY = re.compile(r"^\s*(pass|print\(.*\)|continue|\.\.\.)\s*$")
DEBUG = re.compile(r"\bconsole\.(log|debug|trace|dir)\(|\bdebugger\s*;|\bbreakpoint\(\)|pdb\.set_trace\(|\bdbg!\(|"
                   r"\bvar_dump\(|\bSystem\.out\.print")
DEV_IMPORT = re.compile(r"(import|require|from)\b.*[\"'/.](seed|seeds|fixtures?|mocks?|fakes?|stubs?|__tests__|testing)"
                        r"([\"'/.]|$)")
SECRET = re.compile(r"\b(sk_live_[0-9A-Za-z]{10,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|"
                    r"github_pat_[A-Za-z0-9_]{30,}|xox[abprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35})|"
                    r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
SECRET_FIELD = re.compile(r"(?P<field>password|passwd|secret|api[_-]?key|token|auth)[\"']?\s*[:=]\s*[\"']"
                          r"(?P<value>[^\"'\s$]{6,})[\"']", re.IGNORECASE)
SHOWN = 4
CLOSING = "}"
KINDS = ((8, "loose types or silenced checks", None), (8, "swallowed errors", SWALLOWED), (10, "debug outputs", None),
         (10, "dev or test imports in shipped code", TEST_IN_PROD))


def _mask(value):
    return f"{value[:SHOWN]}... ({len(value)} chars)"


def _self_named(match):
    return match.re is SECRET_FIELD and match.group("value").lower() == match.group("field").lower()


def _secrets(item):
    found = []
    for number, line in enumerate(item["lines"], 1):
        match = SECRET.search(line) or SECRET_FIELD.search(line)
        if match and not _self_named(match):
            found.append((number, _mask(match.group(match.lastindex or 0))))
    return found


def _except_body(rows, number, code):
    indent = len(code) - len(code.lstrip())
    inline = code.split(":", 1)[1].strip()
    body = [inline] if inline else []
    for row in rows[number:]:
        text = row["code"]
        if text.strip() and len(text) - len(text.lstrip()) <= indent:
            break
        body += [text] if text.strip() else []
    return body


def _python_swallowed(rows, number, code):
    body = _except_body(rows, number, code)
    if all(QUIET.match(line) for line in body):
        return True
    return bool(BROAD.match(code)) and all(SILENT_BODY.match(line) for line in body)


def _swallowed(item):
    rows, hits = item["rows"], []
    python = item["path"].suffix == PYTHON_SUFFIX
    for number, row in enumerate(rows, 1):
        code = row["code"]
        closed = OPEN_CATCH.search(code) and number < len(rows) and rows[number]["code"].strip() == CLOSING
        caught = python and EXCEPT.match(code) and _python_swallowed(rows, number, code)
        if EMPTY_CATCH.search(code) or closed or caught:
            hits.append(number)
    return hits


def _scan(item):
    loose, debug, dev = [], [], []
    for number, row in enumerate(item["rows"], 1):
        if LOOSE_TYPE.search(row["code"]) or (is_directive(row["comment"]) and LOOSE_TYPE.search(row["comment"])):
            loose.append(number)
        if not item["test"] and DEBUG.search(row["code"]):
            debug.append(number)
        if not item["test"] and DEV_IMPORT.search(item["lines"][number - 1]) and row["code"].strip():
            dev.append(number)
    return loose, debug, dev


def _finding(item, kind, hits):
    rule, what, cap = kind
    finding = {"rule": rule, "file": item["rel"], "line": hits[0], "what": f"{len(hits)} {what}",
               "proof": "lines " + compact(hits)}
    return {**finding, "cap": cap} if cap else finding


def check(files, root, config):
    findings = []
    for item in files:
        if item["data"] or item["locale"]:
            continue
        for number, masked in _secrets(item):
            findings.append({"rule": 0, "file": item["rel"], "line": number, "cap": "secret", "points": 0,
                             "what": "hardcoded secret", "proof": masked})
        if not item["code"]:
            continue
        loose, debug, dev = _scan(item)
        for kind, hits in zip(KINDS, (loose, _swallowed(item), debug, dev)):
            if hits:
                findings.append(_finding(item, kind, hits))
    return findings, {}
