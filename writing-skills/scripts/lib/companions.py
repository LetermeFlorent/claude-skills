import re

from common import CHECK, NOTE, REFUSE, read_text
from frontmatter import split
from shape import SECTION_LEVEL, classify, french_share, headings, prose

README = "LISEZMOI.md"
TESTED, UNTESTED = "ce qui a été testé", "pas encore testé"
ACCENTS = re.compile(r"[éèêàùçôîâ]")
ENGLISH_LIMIT = 0.5
COMMAND_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*\.md$")
COMMAND_KEYS = ("description", "argument-hint", "allowed-tools")
FALLBACKS = ("$CLAUDE_CONFIG_DIR/skills/", "~/.claude/skills/")
ARGUMENTS = "$ARGUMENTS"
SKILL_TOOL = "Skill"


def _sections(text):
    rows = classify(split(text)[1])
    return {title.strip().lower() for _, level, title in headings(rows) if level == SECTION_LEVEL}, rows


def check_readme_text(text, draft):
    if text is None:
        return [(REFUSE, README, 0, "missing: the French notice for the user")]
    found, (sections, rows) = [], _sections(text)
    if not ACCENTS.search(text):
        found.append((NOTE, README, 0, "no accent anywhere: French prose keeps its accents"))
    if french_share(prose(rows)) < ENGLISH_LIMIT:
        found.append((CHECK, README, 0, "reads as English; LISEZMOI.md is written in French"))
    if draft and TESTED in sections:
        found.append((REFUSE, README, 0, '"Ce qui a été testé" before any test: it is written after the runs'))
    elif not draft and UNTESTED in sections:
        found.append((NOTE, README, 0, 'shipped with "Pas encore testé": the user chose to skip the runs'))
    elif not draft and TESTED not in sections:
        found.append((REFUSE, README, 0, 'no "## Ce qui a été testé" section from the real runs'))
    return found


def _command_front(where, fields):
    if fields is None:
        return [(REFUSE, where, 1, "no front matter between --- lines")]
    found = [(REFUSE, where, 1, f"no {key} in the front matter") for key in COMMAND_KEYS if not fields.get(key)]
    tools = [tool.strip() for tool in fields.get("allowed-tools", "").split(",")]
    if fields.get("allowed-tools") and SKILL_TOOL not in tools:
        found.append((REFUSE, where, 1, "allowed-tools lacks Skill, so the command cannot load its skill"))
    return found


def check_command_text(filename, text, skill_name):
    where = f"commands/{filename}"
    found = []
    if not COMMAND_NAME.match(filename):
        found.append((REFUSE, where, 0, "file name: lowercase ASCII words joined by hyphens"))
    found += [(REFUSE, where, number, "not ASCII: a command file stays without accents")
              for number, line in enumerate(text.splitlines(), 1) if not line.isascii()]
    found += _command_front(where, split(text)[0])
    for base in FALLBACKS:
        if f"{base}{skill_name}/SKILL.md" not in text:
            found.append((REFUSE, where, 0, f"no fallback to {base}{skill_name}/SKILL.md"))
    if ARGUMENTS not in text:
        found.append((REFUSE, where, 0, f"never says what {ARGUMENTS} changes"))
    return found


def check_readme(folder, draft):
    return check_readme_text(read_text(folder / README), draft)


def check_commands(folder, skill_name):
    found = []
    for path in sorted((folder / "commands").glob("*")):
        text = read_text(path)
        if text is None:
            found.append((REFUSE, f"commands/{path.name}", 0, "not readable as UTF-8"))
        else:
            found += check_command_text(path.name, text, skill_name)
    return found
