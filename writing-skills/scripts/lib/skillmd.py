import re

from common import CHECK, NOTE, REFUSE, read_text, relative
from frontmatter import line_of, split
from shape import (LIST, SECTION_LEVEL, TABLE_ROW, TITLE_LEVEL, classify, crowded_headings, french_share, headings,
                   prose, section_rows)

FILE = "SKILL.md"
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_LIMIT, DESCRIPTION_LIMIT, DESCRIPTION_AIM = 64, 1024, 500
LINES_AIM, LINES_LIMIT = 250, 500
TRIGGER_START = "Use when"
STEP_MARKERS = re.compile(r"(?<!-)\bthen\b(?!-)|->|\u2192|\bfollowed by\b"
                          r"|\bstep by step\b|\bafterwards?\b|(?:^|\s)\d[.)]\s",
                          re.IGNORECASE)
FIRST_PERSON = re.compile(r"\b(I|I'm|I'll|my|we|our)\b")
LINE_RULES = ((REFUSE, re.compile(r"\bsuperpowers:[\w-]"), "a superpowers: prefix: name the skill in plain words"),
              (REFUSE, re.compile(r"(?<![\w.])@[\w~./-]+\.md\b"), "an @ path loads the whole file at once"),
              (CHECK, re.compile(r"\bpython3?\s+(?!-I\b)\S*\.py\b"), "a script called without python -I"))
REQUIRED, LAST, RULES, FLAGS = "overview", "files", "rules that never bend", "red flags"
FLAGS_HEADER = "thought"
FRENCH_LIMIT = 0.5
MARKDOWN = "*.md"


def check_description(text, commands, line):
    if not text:
        return [(REFUSE, FILE, line, "no description")]
    found = []
    if not text.startswith(TRIGGER_START):
        found.append((REFUSE, FILE, line, f'the description does not start with "{TRIGGER_START}"'))
    if len(text) > DESCRIPTION_LIMIT:
        found.append((REFUSE, FILE, line, f"the description has {len(text)} characters, {DESCRIPTION_LIMIT} at most"))
    elif len(text) > DESCRIPTION_AIM:
        found.append((NOTE, FILE, line, f"the description has {len(text)} characters and loads in every session"))
    for command in commands:
        if f"/{command}" not in text:
            found.append((REFUSE, FILE, line, f"the description does not name /{command}"))
    for marker in sorted({match.group(0).strip() for match in STEP_MARKERS.finditer(text)}):
        found.append((CHECK, FILE, line, f'the description holds "{marker}": a trigger, or a step of the procedure?'))
    if FIRST_PERSON.search(text):
        found.append((CHECK, FILE, line, "the description speaks in the first person; it is read in the third"))
    return found


def check_front(fields, text, folder_name, commands):
    if fields is None:
        return [(REFUSE, FILE, 1, "no front matter between --- lines")]
    found, name, line = [], fields.get("name", ""), line_of(text, "name")
    if not NAME.match(name) or len(name) > NAME_LIMIT:
        found.append((REFUSE, FILE, line, f"name {name!r}: lowercase letters, digits, hyphens, {NAME_LIMIT} at most"))
    elif name != folder_name:
        found.append((REFUSE, FILE, line, f"name {name!r} is not the folder's name {folder_name!r}"))
    return found + check_description(fields.get("description", ""), commands, line_of(text, "description"))


def _red_flags(rows):
    table = [line for _, line, kind in section_rows(rows, FLAGS) if TABLE_ROW.match(line)]
    first = table[0].strip("| \t").split("|")[0].strip().lower() if table else ""
    return [] if first == FLAGS_HEADER else [(NOTE, FILE, 0, "## Red flags is not a | Thought | Reality | table")]


def check_body(rows, total):
    found, titles = [], headings(rows)
    if not titles or titles[0][1] != TITLE_LEVEL:
        found.append((REFUSE, FILE, titles[0][0] if titles else 1, "the body does not open on a # title"))
    seconds = [(number, text.strip().lower()) for number, level, text in titles if level == SECTION_LEVEL]
    names = [name for _, name in seconds]
    if REQUIRED not in names:
        found.append((REFUSE, FILE, 0, "no ## Overview section"))
    if seconds and names[-1] != LAST:
        found.append((NOTE, FILE, seconds[-1][0], "## Files is not the last section"))
    if RULES in names and FLAGS not in names:
        found.append((NOTE, FILE, 0, "hard rules but no ## Red flags table"))
    elif FLAGS in names:
        found += _red_flags(rows)
    found += [(REFUSE if kind == LIST else NOTE, FILE, number, f"a {kind} right under a heading: a sentence first")
              for number, kind in crowded_headings(rows)]
    if total > LINES_LIMIT:
        found.append((REFUSE, FILE, 0, f"{total} lines, {LINES_LIMIT} at most: move material to reference/"))
    elif total > LINES_AIM:
        found.append((NOTE, FILE, 0, f"{total} lines, about {LINES_AIM} is the aim"))
    return found


def check_lines(lines):
    found = []
    for number, line in enumerate(lines, 1):
        found += [(level, FILE, number, message) for level, pattern, message in LINE_RULES if pattern.search(line)]
    return found


def check_skill_md(folder, commands):
    text = read_text(folder / FILE)
    if text is None:
        return [(REFUSE, FILE, 0, "missing or not UTF-8")]
    fields, body, offset = split(text)
    rows = classify(body, offset + 1)
    found = check_front(fields, text, folder.name, commands) + check_body(rows, len(text.splitlines()))
    if french_share(prose(rows)) > FRENCH_LIMIT:
        found.append((CHECK, FILE, 0, "reads as French; SKILL.md is written in English"))
    return found + check_lines(text.splitlines())


def command_names(folder):
    return [path.stem for path in sorted((folder / "commands").glob(MARKDOWN))]


def owned_paths(folder):
    patterns = (f"reference/{MARKDOWN}", MARKDOWN, "scripts/*.py")
    skipped = {FILE, "LISEZMOI.md"}
    return [relative(path, folder) for pattern in patterns for path in sorted(folder.glob(pattern))
            if path.name not in skipped]
