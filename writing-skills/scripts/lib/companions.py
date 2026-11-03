import re

from common import CHECK, NOTE, REFUSE, read_text
from frontmatter import split
from shape import classify, french_share, prose

README = "LISEZMOI.md"
ACCENTS = re.compile(r"[éèêàùçôîâ]")
ENGLISH_LIMIT = 0.5
COMMAND_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*\.md$")
COMMAND_KEYS = ("description", "argument-hint", "allowed-tools")
ARGUMENTS = "$ARGUMENTS"
SKILL_TOOL = "Skill"


def check_readme_text(text):
    if text is None:
        return [(REFUSE, README, 0, "missing: the French notice for the user")]
    found = []
    if not ACCENTS.search(text):
        found.append((NOTE, README, 0, "no accent anywhere: French prose keeps its accents"))
    if french_share(prose(classify(text.splitlines()))) < ENGLISH_LIMIT:
        found.append((CHECK, README, 0, "reads as English; LISEZMOI.md is written in French"))
    return found


def _command_front(where, fields):
    if fields is None:
        return [(REFUSE, where, 1, "no front matter between --- lines")]
    found = [(REFUSE, where, 1, f"no {key} in the front matter") for key in COMMAND_KEYS if not fields.get(key)]
    tools = [tool.strip() for tool in fields.get("allowed-tools", "").split(",")]
    if fields.get("allowed-tools") and SKILL_TOOL not in tools:
        found.append((REFUSE, where, 1, "allowed-tools lacks Skill, so the command cannot load its skill"))
    return found


def check_command_text(filename, text):
    where = f"commands/{filename}"
    found = []
    if not COMMAND_NAME.match(filename):
        found.append((REFUSE, where, 0, "file name: lowercase ASCII words joined by hyphens"))
    found += [(REFUSE, where, number, "not ASCII: a command file stays without accents")
              for number, line in enumerate(text.splitlines(), 1) if not line.isascii()]
    found += _command_front(where, split(text)[0])
    if ARGUMENTS not in text:
        found.append((REFUSE, where, 0, f"never says what {ARGUMENTS} changes"))
    return found


def check_readme(folder):
    return check_readme_text(read_text(folder / README))


def check_commands(folder):
    found = []
    for path in sorted((folder / "commands").glob("*")):
        text = read_text(path)
        if text is None:
            found.append((REFUSE, f"commands/{path.name}", 0, "not readable as UTF-8"))
        else:
            found += check_command_text(path.name, text)
    return found
