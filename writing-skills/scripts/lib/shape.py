import re

FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING = re.compile(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*#*\s*$")
LIST_ITEM = re.compile(r"^\s*([-*+]|\d+[.)])\s+")
TABLE_ROW = re.compile(r"^\s*\|")
WORD = re.compile(r"[^\W\d_]+")
FRENCH_WORDS = frozenset("le la les des une est et du dans pour que qui avec sur pas ce il elle au".split())
ENGLISH_WORDS = frozenset("the and is are of to with for that this when not it an be".split())
UNDECIDED = 0.5
TEXT, CODE = "text", "code"
LIST, TABLE = "list", "table"
TITLE_LEVEL, SECTION_LEVEL = 1, 2


def _closes(line, fence):
    stripped = line.strip()
    marks = len(stripped) - len(stripped.lstrip(fence[0]))
    return marks >= len(fence) and not stripped[marks:].strip()


def classify(lines, start=1):
    fence, rows = None, []
    for number, line in enumerate(lines, start):
        opened = FENCE.match(line)
        if fence is None and opened:
            fence, kind = opened.group(1), CODE
        elif fence is not None:
            kind = CODE
            if opened and _closes(line, fence):
                fence = None
        else:
            kind = TEXT
        rows.append((number, line, kind))
    return rows


def headings(rows):
    found = []
    for number, line, kind in rows:
        match = HEADING.match(line) if kind == TEXT else None
        if match:
            found.append((number, len(match["marks"]), match["title"]))
    return found


def crowded_headings(rows):
    flagged = []
    for index, (number, line, kind) in enumerate(rows):
        if kind != TEXT or not HEADING.match(line):
            continue
        after = next((row for row in rows[index + 1:] if row[1].strip()), None)
        if after and after[2] == TEXT and LIST_ITEM.match(after[1]):
            flagged.append((number, LIST))
        elif after and after[2] == TEXT and TABLE_ROW.match(after[1]):
            flagged.append((number, TABLE))
    return flagged


def section_rows(rows, title):
    inside, kept = False, []
    for number, line, kind in rows:
        match = HEADING.match(line) if kind == TEXT else None
        if match and len(match["marks"]) <= SECTION_LEVEL:
            inside = match["title"].strip().lower() == title
            continue
        if inside:
            kept.append((number, line, kind))
    return kept


def french_share(text):
    words = [word.lower() for word in WORD.findall(text)]
    french = sum(1 for word in words if word in FRENCH_WORDS)
    english = sum(1 for word in words if word in ENGLISH_WORDS)
    return french / (french + english) if french + english else UNDECIDED


def prose(rows):
    return "\n".join(line for _, line, kind in rows if kind == TEXT)
