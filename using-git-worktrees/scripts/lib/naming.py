import re
from collections import Counter

TOOLS = "claude|codex|copilot|cursor|devin|jules|gemini|aider|windsurf|kiro|amazonq|openhands|cline|junie"
FORBIDDEN = re.compile(rf"(^|/)({TOOLS})[/-]", re.I)
SHARED = {"main", "master", "develop", "trunk", "dev"}
VALID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
MAX_SLUG = 40
MIN_PREFIX_USES = 2


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:MAX_SLUG].strip("-")


def short_names(names):
    return [name.split("/", 1)[1] if name.startswith("origin/") else name for name in names]


def convention(names):
    work = [name for name in short_names(names) if name not in SHARED and not FORBIDDEN.search(name)]
    counts = Counter(name.split("/")[0] + "/" for name in work if "/" in name)
    if not counts:
        return ""
    prefix, uses = counts.most_common(1)[0]
    return prefix if uses >= MIN_PREFIX_USES and uses * 2 >= len(work) else ""


def problems(name, existing):
    found = []
    if FORBIDDEN.search(name):
        found.append(f"branch '{name}' carries a tool name followed by / or - ({TOOLS.replace('|', ', ')})")
    if not VALID.match(name) or ".." in name or name.endswith((".lock", "/", ".")):
        found.append(f"branch '{name}' is not a valid name")
    if name in short_names(existing):
        found.append(f"branch '{name}' already exists")
    return found
