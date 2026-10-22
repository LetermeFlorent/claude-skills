import re

from patterns import (CURLY, EMOJI, FRENCH_QUOTES, HAND_TYPOGRAPHY, INVISIBLE, PHRASES, PLACEHOLDER, RESIDUE,
                      SIGNATURE, SPACES, STRAIGHT, VOCABULARY)

INLINE_CODE = re.compile(r"(`+).+?\1")
SAFE = (("quotes", CURLY), ("invisible", INVISIBLE), ("space", SPACES))
LINE = (("signature", SIGNATURE), ("residue", RESIDUE), ("placeholder", PLACEHOLDER), ("emoji", EMOJI),
        ("em dash", HAND_TYPOGRAPHY))
PROSE = (("vocabulary", VOCABULARY), ("phrase", PHRASES))
DETAILED = ("vocabulary", "phrase", "residue", "signature", "placeholder")


def _quoted(match):
    return '"' + match.group(1).strip() + '"'


def clean(text):
    text = FRENCH_QUOTES.sub(_quoted, text).translate(STRAIGHT)
    return SPACES.sub(" ", INVISIBLE.sub("", text))


def _segments(line):
    start = 0
    for match in INLINE_CODE.finditer(line):
        yield line[start:match.start()], False
        yield match.group(0), True
        start = match.end()
    yield line[start:], False


def fix_line(line):
    fixed = "".join(piece if code else clean(piece) for piece, code in _segments(line))
    kinds = [kind for kind, pattern in SAFE if pattern.search(outside_code(line))]
    return fixed, kinds if fixed != line else []


def outside_code(line):
    return INLINE_CODE.sub("", line)


def line_markers(text, prose):
    checks = LINE + PROSE if prose else LINE
    found = []
    for kind, pattern in checks:
        matches = sorted({match.group(0).strip().lower() for match in pattern.finditer(text)})
        if matches:
            found.append(f"{kind}: {', '.join(matches)}" if kind in DETAILED else kind)
    return found


def safe_markers(text):
    return [kind for kind, pattern in SAFE if pattern.search(text)]
