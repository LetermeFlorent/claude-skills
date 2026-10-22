import re

FRONT_MATTER = "---"
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
RULE_LINE = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")
HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
SETEXT = re.compile(r"^\s{0,3}(=+|-+)\s*$")
INLINE_CODE = re.compile(r"(`+).+?\1")
LIST_ITEM = re.compile(r"^\s*([-*+]|\d+[.)])\s+")
BOLD_LEAD = re.compile(r"^\s*([-*+]|\d+[.)])\s+\*\*[^*]+\*\*\s*[:.]|^\s*([-*+]|\d+[.)])\s+\*\*[^*]+[:.]\*\*")
BADGE = re.compile(r"img\.shields\.io|badge\.fury\.io|badgen\.net|forthebadge\.com")
CALLOUT = re.compile(r"^\s*>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]", re.IGNORECASE)
HTML_RULE = re.compile(r"<hr\b|wp:separator|wp-block-separator", re.IGNORECASE)
WORD = re.compile(r"[^\W\d_][\w'-]*")
SMALL_WORDS = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "of", "on", "or", "the", "to", "with", "vs",
               "via", "de", "des", "du", "la", "le", "les", "et", "en", "un", "une", "au", "aux", "pour", "sur"}
STOCK_OUTLINE = {"overview", "features", "tech stack", "installation", "usage", "contributing", "license",
                 "contact", "getting started", "prerequisites", "roadmap", "acknowledgments", "acknowledgements"}
STOCK_MINIMUM = 5
TITLE_MINIMUM = 3
SHORT_DOCUMENT = 150
TABLE_OF_CONTENTS = re.compile(r"^(table of contents|contents|sommaire|table des mati[eè]res)$", re.IGNORECASE)


def prose_lines(lines):
    front = bool(lines) and lines[0].strip() == FRONT_MATTER
    fence = None
    for number, line in enumerate(lines, 1):
        if front:
            front = number == 1 or line.strip() != FRONT_MATTER
            continue
        opened = FENCE.match(line)
        if opened and fence is None:
            fence = opened.group(1)
            continue
        if fence is not None:
            if opened and opened.group(1)[0] == fence[0] and len(opened.group(1)) >= len(fence) \
                    and not opened.group(2).strip():
                fence = None
            continue
        yield number, line


def nested_fences(lines):
    found, fence = [], None
    for number, line in enumerate(lines, 1):
        opened = FENCE.match(line)
        if not opened:
            continue
        marks, info = opened.group(1), opened.group(2).strip()
        if fence is None:
            fence = marks
        elif marks[0] == fence[0] and len(marks) >= len(fence) and not info:
            fence = None
        elif marks[0] == fence[0] and len(marks) == len(fence) and info:
            found.append(number)
    return found


def separators(lines):
    kept = dict(prose_lines(lines))
    return [number for number in kept if RULE_LINE.match(kept[number]) and
            (number == 1 or not lines[number - 2].strip())]


def _title_case(text):
    words = [word for word in WORD.findall(text) if word.lower() not in SMALL_WORDS]
    capital = [word for word in words[1:] if word[0].isupper() and not word.isupper()]
    return len(words) >= TITLE_MINIMUM and len(capital) == len(words) - 1


def structure(lines):
    found, prose = {}, list(prose_lines(lines))
    headings = {number: HEADING.match(line).group(2) for number, line in prose if HEADING.match(line)}
    following = {number: line for number, line in prose}
    headings.update({number: line.strip() for number, line in prose if line.strip() and not LIST_ITEM.match(line)
                     and SETEXT.match(following.get(number + 1, "")) and number not in headings})
    for number, text in headings.items():
        if _title_case(text):
            found.setdefault("title case heading", []).append(number)
        after = following.get(number + 1, "") or following.get(number + 2, "")
        if LIST_ITEM.match(after):
            found.setdefault("list right under a heading", []).append(number)
    for number, line in prose:
        for kind, pattern in (("bold lead-in", BOLD_LEAD), ("shields badge", BADGE), ("callout block", CALLOUT),
                              ("html rule", HTML_RULE)):
            if pattern.search(INLINE_CODE.sub("", line)):
                found.setdefault(kind, []).append(number)
    names = {text.strip().lower() for text in headings.values()}
    if len(names & STOCK_OUTLINE) >= STOCK_MINIMUM:
        found["stock readme outline"] = [min(headings)]
    toc = [number for number, text in headings.items() if TABLE_OF_CONTENTS.match(text.strip())]
    if toc and len(lines) < SHORT_DOCUMENT:
        found["table of contents on a short page"] = toc
    return found


def drop_separators(lines, numbers):
    dropped = set(numbers)
    kept = []
    for number, line in enumerate(lines, 1):
        if number in dropped:
            continue
        if kept and not kept[-1].strip() and not line.strip() and number - 1 in dropped:
            continue
        kept.append(line)
    return kept
