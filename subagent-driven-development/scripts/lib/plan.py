import re
from itertools import combinations

FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
TASK = re.compile(r"^task\s+(\d+)\b\W*(.*)$", re.IGNORECASE)
FILE_LINE = re.compile(r"^\s*[-*]\s*\**(create|modify|test|delete|rename)\**\s*:\s*\**\s*`([^`]+)`", re.IGNORECASE)
LINE_RANGE = re.compile(r":\d+(-\d+)?$")
HARD_LINE = re.compile(r"^\W*difficulty\W*\s*hard\b", re.IGNORECASE)
HARD_WORD = re.compile(r"\bhard\b", re.IGNORECASE)
SPEC = re.compile(r"^\s*(?:[-*]\s*)?\**spec\**\s*:\s*\**\s*(.+?)\s*$", re.IGNORECASE)
CONSTRAINTS = "global constraints"
QUOTES = "`*\"' "


def fenced(lines):
    inside, opener, flags = False, "", []
    for line in lines:
        match = FENCE.match(line)
        bare = line.strip()
        if match and not inside:
            inside, opener = True, match.group(1)
            flags.append(True)
        elif inside and set(bare) == {opener[0]} and len(bare) >= len(opener):
            inside = False
            flags.append(True)
        else:
            flags.append(inside)
    return flags


def headings(lines):
    flags = fenced(lines)
    found = []
    for index, line in enumerate(lines):
        match = None if flags[index] else HEADING.match(line)
        if match:
            found.append((index, len(match.group(1)), match.group(2)))
    return found


def _end(heads, position, level):
    later = heads[position + 1:]
    return next((index for index, other, text in later if other <= level or TASK.match(text)), None)


def tasks(lines):
    heads, found = headings(lines), []
    for position, (index, level, text) in enumerate(heads):
        match = TASK.match(text)
        if match:
            end = _end(heads, position, level)
            found.append({"number": int(match.group(1)), "title": match.group(2).strip(), "start": index,
                          "end": len(lines) if end is None else end})
    return found


def section(lines, name):
    heads = headings(lines)
    for position, (index, level, text) in enumerate(heads):
        if text.strip().lower() == name:
            end = _end(heads, position, level)
            return lines[index:len(lines) if end is None else end]
    return []


def body(lines, task):
    return lines[task["start"]:task["end"]]


def files_of(part):
    flags = fenced(part)
    found = []
    for index, line in enumerate(part):
        match = None if flags[index] else FILE_LINE.match(line)
        if match:
            found.append(LINE_RANGE.sub("", match.group(2).strip()))
    return list(dict.fromkeys(found))


def is_hard(task, part):
    flags = fenced(part)
    return bool(HARD_WORD.search(task["title"])) or any(
        HARD_LINE.match(line) for index, line in enumerate(part) if not flags[index])


def shared(files_by_task):
    pairs = []
    for (left, left_files), (right, right_files) in combinations(files_by_task.items(), 2):
        common = sorted(set(left_files) & set(right_files))
        if common:
            pairs.append((left, right, common))
    return pairs


def spec(lines):
    flags = fenced(lines)
    for index, line in enumerate(lines):
        match = None if flags[index] else SPEC.match(line)
        if match:
            return match.group(1).strip(QUOTES) or None
    return None
