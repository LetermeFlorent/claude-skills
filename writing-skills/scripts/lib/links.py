import re

from common import CHECK, NOTE

FILE = "SKILL.md"
TOKEN = re.compile(r"`([^`\s]+)`")
TEMPLATE_MARKS = set("<>*{}$")
LOCAL_DIRS = ("scripts/", "reference/", "commands/", "tests/", "templates/", "examples/")
ROOT_FILE = re.compile(r"^[\w-]+-(brief|template)\.md$")


def referenced(text):
    found = set()
    for token in TOKEN.findall(text):
        if TEMPLATE_MARKS & set(token):
            continue
        if token.startswith(LOCAL_DIRS) or ROOT_FILE.match(token):
            found.add(token.rstrip("/"))
    return sorted(found)


def missing(text, exists):
    return [(CHECK, FILE, 0, f"`{token}` is not in this folder; fine only if it names another skill's file")
            for token in referenced(text) if not exists(token)]


def orphans(text, owned):
    return [(NOTE, path, 0, "never named in SKILL.md, so no agent will open it")
            for path in owned if path not in text and path.rsplit("/", 1)[-1] not in text]


def check_links(folder, text, owned):
    return missing(text, lambda token: (folder / token).exists()) + orphans(text, owned)
