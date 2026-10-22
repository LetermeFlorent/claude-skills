import re

SPEC_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*-design\.md$")
SPEC_PARENTS = ("specs", ".ia")
MARKERS = re.compile(r"\b(?:TBD|TODO|FIXME|XXX)\b|\?\?\?|\[\.\.\.\]|<\.\.\.>|\(\.\.\.\)")
FRENCH_MARKERS = re.compile(r"\b(?:à|a) (?:définir|definir|préciser|preciser|compléter|completer)\b",
                            re.IGNORECASE)
HEADING = re.compile(r"^(#{1,6})\s+\S")
FENCE = re.compile(r"^\s*(```|~~~)")
EXPECTED = "<repo>/.ia/specs/YYYY-MM-DD-<topic>-design.md"


def name_problems(path):
    problems = []
    if not SPEC_NAME.match(path.name):
        problems.append(f"name {path.name} does not follow {EXPECTED}")
    parents = (path.parent.name, path.parent.parent.name)
    if parents != SPEC_PARENTS:
        problems.append(f"{path.as_posix()} is not in {EXPECTED}")
    return problems


def prose_lines(lines):
    inside = False
    for number, line in enumerate(lines, 1):
        if FENCE.match(line):
            inside = not inside
            yield number, line
            continue
        if not inside:
            yield number, line


def placeholders(lines):
    return [number for number, line in prose_lines(lines) if MARKERS.search(line) or FRENCH_MARKERS.search(line)]


def prose_rows(lines):
    found = []
    for number, line in prose_lines(lines):
        match = HEADING.match(line)
        found.append((number, len(match.group(1)) if match else 0, bool(line.strip())))
    return found


def empty_sections(lines):
    rows = [row for row in prose_rows(lines) if row[2]]
    empty = []
    for index, (number, level, _) in enumerate(rows):
        if not level:
            continue
        following = rows[index + 1] if index + 1 < len(rows) else None
        if following is None or 0 < following[1] <= level:
            empty.append(number)
    return empty


def content_problems(lines):
    problems = []
    if not any(HEADING.match(line) for line in lines):
        problems.append("no heading: the spec needs a title and sections")
    problems += [f"line {number}: placeholder left in the spec" for number in placeholders(lines)]
    problems += [f"line {number}: section with nothing under it" for number in empty_sections(lines)]
    return problems
