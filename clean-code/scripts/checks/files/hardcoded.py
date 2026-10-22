import re
from collections import defaultdict

from common import compact
from lexer import EMPTY_STRING, balance

RULE = 18
NUMBER = re.compile(r"(?<![\w.$#\[])-?(0[xX][0-9a-fA-F]+|\d[\d_]*(\.\d+)?([eE][+-]?\d+)?)(?![\w.\]])")
NEUTRAL = {"0", "1", "-1", "0.0", "1.0"}
CONSTANT = re.compile(r"^\s*(export\s+)?((public|private|protected|internal|static|readonly|final|const|val|let|var|"
                      r"pub)\s+)*[A-Z][A-Z0-9_]*(\s*,\s*[A-Z][A-Z0-9_]*)*\s*(:[^=]+)?=|^\s*(enum\b|const\s*\()|"
                      r"^\s*[A-Z][A-Z0-9_]*\s*,?\s*$")
IMPORT = re.compile(r"^\s*(import|from|#include|using|package|require|use)\b|require\(")
ENVIRONMENT = re.compile(r"^(https?|wss?|postgres(ql)?|mysql|mongodb|redis|amqp|ftp)://|localhost|127\.0\.0\.1|"
                         r"^[A-Za-z]:[\\/]|^/(home|Users|tmp|var|etc|opt|mnt)/|^[\w.+-]+@[\w-]+\.[\w.]+$")
READS_ENV = re.compile(r"process\.env|os\.environ|getenv|import\.meta\.env|System\.getenv|env::var|ENV\[")
MAIN_GUARD = re.compile(r"__name__\s*==")
COMPARED_BEFORE = re.compile(r"(===?|!==?)\s*$|\bcase\s*$")
COMPARED_AFTER = re.compile(r"^\s*(===?|!==?)")
SKIPPED = {".css", ".scss", ".less", ".html", ".sql", ".sh", ".bash", ".ps1", ".vue", ".svelte"}
SUBSCRIPT = re.compile(r"\[\s*$")
LOOKUP = re.compile(r"\.(get|pop|setdefault|group)\(\s*$")
ENTRY = re.compile(r"(^|[{,])\s*$")
PATTERN_CALL = re.compile(r"\bre\.(compile|search|match|sub|findall)\(|\bnew\s+RegExp\(|\bRegex\(")
FLAG = re.compile(r"^--?[A-Za-z][\w-]*$")
WORDLIKE = re.compile(r"\w")
SHORTEST = 3


def _compared(code, strings):
    pieces, hits = code.split(EMPTY_STRING), 0
    for index, text in enumerate(strings[:len(pieces) - 1]):
        compared = COMPARED_BEFORE.search(pieces[index]) or COMPARED_AFTER.search(pieces[index + 1])
        if WORDLIKE.search(text) and compared:
            hits += 1
    return hits


def _keyed(code):
    pieces = code.split(EMPTY_STRING)
    return {index for index in range(len(pieces) - 1)
            if (SUBSCRIPT.search(pieces[index]) and pieces[index + 1].startswith("]")) or LOOKUP.search(pieces[index])
            or (ENTRY.search(pieces[index]) and pieces[index + 1].lstrip().startswith(":"))}


def _scan(item):
    kinds, seen, depth = defaultdict(list), defaultdict(list), 0
    for number, (row, line) in enumerate(zip(item["rows"], item["lines"]), 1):
        code = row["code"]
        declared = depth > 0 or bool(CONSTANT.match(code))
        depth = max(0, depth + balance(code)) if declared else 0
        if IMPORT.search(code) or MAIN_GUARD.search(code) or not code.strip():
            continue
        keyed = _keyed(code)
        for position, text in enumerate(row["strings"]):
            if ENVIRONMENT.search(text) and not READS_ENV.search(line) and not PATTERN_CALL.search(code):
                kinds["environment values"].append(number)
            elif len(text.strip()) >= SHORTEST and not declared and position not in keyed and not FLAG.match(text):
                seen[text].append(number)
        if declared:
            continue
        if any(match.group(0) not in NEUTRAL for match in NUMBER.finditer(code)):
            kinds["numbers"].append(number)
        if _compared(code, row["strings"]):
            kinds["literal comparisons"].append(number)
    for text, numbers in seen.items():
        if len(numbers) > 1:
            kinds[f"repeated {text!r}"].extend(numbers)
    return kinds


def check(files, root, config):
    findings, carrying, counted = [], 0, 0
    for item in files:
        if not item["code"] or item["test"] or item["data"] or item["path"].suffix.lower() in SKIPPED:
            continue
        counted += 1
        kinds = _scan(item)
        if not kinds:
            continue
        carrying += 1
        total = sum(map(len, kinds.values()))
        first = min(min(numbers) for numbers in kinds.values())
        proof = "; ".join(f"{kind} {compact(numbers)}" for kind, numbers in sorted(kinds.items()))
        findings.append({"rule": RULE, "file": item["rel"], "line": first, "what": f"{total} hardcoded values",
                         "proof": proof})
    return findings, {"files_with_hardcoded": carrying, "valued_files": counted}
