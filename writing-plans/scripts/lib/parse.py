import re

TASK = re.compile(r"^### Task (\d+): (.+)$", re.MULTILINE)
FILE_LINE = re.compile(r"^[ \t]*- (Create|Modify|Delete|Test): `([^`]+)`(.*)$", re.MULTILINE)
STEP = re.compile(r"^- \[[ x]\] Step (\d+): (.+)$", re.MULTILINE)
PATHS_LINE = re.compile(r"^[ \t]*Paths: (.+)$", re.MULTILINE)
NO_TEST = re.compile(r"^No test: (.+)$", re.MULTILINE)
LINE_RANGE = re.compile(r":\d+(-\d+)?$")
TICKS = re.compile(r"`([^`]+)`")
SIZE_NOTE = re.compile(r"about (\d+) lines")
LABEL = re.compile(r"^(Goal|Architecture|Stack|Spec): (.+)$", re.MULTILINE)


def strip_range(raw):
    return LINE_RANGE.sub("", raw.strip())


def split_tasks(text):
    marks = list(TASK.finditer(text))
    header = text[: marks[0].start()] if marks else text
    tasks = []
    for index, mark in enumerate(marks):
        end = marks[index + 1].start() if index + 1 < len(marks) else len(text)
        tasks.append({"number": int(mark.group(1)), "title": mark.group(2), "body": text[mark.end():end]})
    return header, tasks


def task_files(body):
    return [(kind, strip_range(path), note) for kind, path, note in FILE_LINE.findall(body)]


def task_steps(body):
    marks = list(STEP.finditer(body))
    steps = []
    for index, mark in enumerate(marks):
        end = marks[index + 1].start() if index + 1 < len(marks) else len(body)
        steps.append({"number": int(mark.group(1)), "title": mark.group(2), "text": body[mark.end():end]})
    return steps


def commit_paths(step_text):
    found = PATHS_LINE.search(step_text)
    if not found:
        return None
    return {strip_range(item) for item in TICKS.findall(found.group(1))}


def header_labels(header):
    return {name for name, _ in LABEL.findall(header)}
