import re

FOLDER = (".ia", "references")
INDEX = "references.md"
TO_DESCRIBE = "(à décrire)"
HEADER = ("# Références\n\nUne ligne par image : ce qu'il faut en reprendre, et ce qu'il ne faut pas "
          "reprendre.\n\n")
ENTRY = re.compile(r"^- (.+?) : (.*)$")
SECTION = "## "


def entries(text):
    found = {}
    for line in text.splitlines():
        if line.startswith(SECTION):
            break
        match = ENTRY.match(line.strip())
        if match:
            found[match.group(1).strip("`")] = match.group(2).strip()
    return found


def with_lines(text, names):
    known = entries(text)
    new = [f"- {name} : {TO_DESCRIBE}" for name in names if name not in known]
    if not new:
        return text
    lines = (text or HEADER).splitlines()
    cut = next((i for i, line in enumerate(lines) if line.startswith(SECTION)), len(lines))
    head = lines[:cut]
    while head and not head[-1].strip():
        head.pop()
    glue = [] if head and ENTRY.match(head[-1]) else [""]
    tail = [""] + lines[cut:] if cut < len(lines) else []
    return "\n".join(head + glue + new + tail) + "\n"


def problems(text, files):
    known = entries(text)
    found = []
    for name, picture in sorted(files.items()):
        if picture is None:
            found.append(f"{name} is not an image: move it out of the references folder")
        elif name not in known:
            found.append(f"{name} has no line in {INDEX}")
        elif not known[name] or known[name] == TO_DESCRIBE:
            found.append(f"write in {INDEX} what to take from {name}")
    for name in sorted(set(known) - set(files)):
        found.append(f"{INDEX} names {name}, which is not in the folder")
    return found
