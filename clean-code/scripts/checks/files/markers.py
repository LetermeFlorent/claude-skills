import re

from common import compact
from store import ATTRIBUTION
from words import AI_SIGNATURE

RULE = 13
TYPOGRAPHY_POINTS = (0x2014, 0x2015, 0x2018, 0x2019, 0x201C, 0x201D, 0xAB, 0xBB, 0xA0, 0x202F, (0x2002, 0x200F),
                     0xAD, 0xFEFF, 0x180E, 0x205F, (0x202A, 0x202E), (0x2060, 0x2064), (0x2066, 0x2069),
                     (0xFE00, 0xFE0F), (0xE000, 0xF8FF), (0xE0000, 0xE007F), (0xE0100, 0xE01EF))
EMOJI_POINTS = ((0x1F300, 0x1FAFF), (0x2600, 0x27BF), 0x2B50, 0x2B55, 0x2B1B, 0x2B1C)


def _chars(points):
    return "".join(chr(point) if isinstance(point, int) else f"{chr(point[0])}-{chr(point[1])}" for point in points)


TYPOGRAPHY = re.compile(f"[{_chars(TYPOGRAPHY_POINTS)}]")
EMOJI = re.compile(f"[{_chars(EMOJI_POINTS)}]")
PLACEHOLDER = re.compile(r"\.\.\.\s*(existing|rest of( the)?) code\s*\.\.\.|TODO:?\s*implement|Example usage|"
                         r"</?think>|let'?s think step by step|as an ai language model|oaicite|contentReference\[|"
                         r"\bturn\d+(search|view|news|fetch)\d+|utm_source=(chatgpt\.com|openai)|\[cite:\s*\d+|"
                         r"grok_card|\[web:\d+\]", re.IGNORECASE)
UI_DEFAULT = re.compile(r"font-family:[^;]*\b(Inter|Space Grotesk|Geist|Instrument Serif)\b|\bindigo-\d{3}\b|#6366f1|"
                        r"#8b5cf6|#a855f7|#4f46e5|backdrop-filter|from-indigo|to-purple-|to-violet-|bg-clip-text",
                        re.IGNORECASE)
UI_SUFFIXES = {".css", ".scss", ".less", ".html", ".tsx", ".jsx", ".vue", ".svelte"}
BADGE = re.compile(r"img\.shields\.io|badge\.fury\.io|badgen\.net")
RULE_LINE = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"(`+).+?\1")
FRONT_MATTER = "---"
HR = re.compile(r"<hr\b|wp:separator|wp-block-separator", re.IGNORECASE)


def _prose(lines):
    kinds, fenced = {}, False
    front = bool(lines) and lines[0].strip() == FRONT_MATTER
    for number, line in enumerate(lines, 1):
        if front:
            front = number == 1 or line.strip() != FRONT_MATTER
            continue
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        previous = lines[number - 2].strip() if number > 1 else ""
        if RULE_LINE.match(line) and not previous:
            kinds.setdefault("rule line", []).append(number)
        if BADGE.search(line):
            kinds.setdefault("shields badge", []).append(number)
        _common(INLINE_CODE.sub("", line), number, kinds)
    return kinds


def _common(text, number, kinds):
    for kind, pattern in (("typography", TYPOGRAPHY), ("emoji", EMOJI), ("placeholder", PLACEHOLDER),
                          ("separator", HR)):
        if pattern.search(text):
            kinds.setdefault(kind, []).append(number)


def _code(item):
    kinds = {}
    ui = item["path"].suffix.lower() in UI_SUFFIXES
    for number, (row, line) in enumerate(zip(item["rows"], item["lines"]), 1):
        _common(row["comment"] + " " + row["code"], number, kinds)
        if any(EMOJI.search(piece) for piece in row["strings"]):
            kinds.setdefault("emoji", []).append(number)
        if ui and UI_DEFAULT.search(line):
            kinds.setdefault("ui default", []).append(number)
    return kinds


def _attribution(item):
    return [number for number, line in enumerate(item["lines"], 1) if AI_SIGNATURE.search(line)]


def check(files, root, config):
    findings, carrying, scanned = [], 0, 0
    for item in files:
        if item["locale"] or item["data"] or not (item["code"] or item["prose"]):
            continue
        scanned += 1
        kinds = _code(item) if item["code"] else _prose(item["lines"])
        signed = _attribution(item)
        if signed:
            findings.append({"rule": RULE, "file": item["rel"], "line": signed[0], "cap": ATTRIBUTION,
                             "what": "AI tool attribution", "proof": "lines " + compact(signed)})
        if not kinds:
            continue
        carrying += 1
        first = min(min(lines) for lines in kinds.values())
        what = ", ".join(f"{kind} {compact(lines)}" for kind, lines in sorted(kinds.items()))
        findings.append({"rule": RULE, "file": item["rel"], "line": first,
                         "what": f"{sum(map(len, kinds.values()))} AI markers", "proof": what})
    return findings, {"marker_files": carrying, "marker_scanned": scanned}
