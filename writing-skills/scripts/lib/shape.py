import re

FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING = re.compile(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*#*\s*$")
WORD = re.compile(r"[^\W\d_]+")
FRENCH_WORDS = frozenset("le la les des une est et du dans pour que qui avec sur pas ce il elle au".split())
ENGLISH_WORDS = frozenset("the and is are of to with for that this when not it an be".split())
UNDECIDED = 0.5
TEXT, CODE = "text", "code"
TITLE_LEVEL = 1


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


def french_share(text):
    words = [word.lower() for word in WORD.findall(text)]
    french = sum(1 for word in words if word in FRENCH_WORDS)
    english = sum(1 for word in words if word in ENGLISH_WORDS)
    return french / (french + english) if french + english else UNDECIDED


def prose(rows):
    return "\n".join(line for _, line, kind in rows if kind == TEXT)
