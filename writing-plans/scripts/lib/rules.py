import re

from parse import NO_TEST, SIZE_NOTE, commit_paths, header_labels, task_files, task_steps

LABELS = ("Goal", "Architecture", "Stack", "Spec")
SECTIONS = ("## Global constraints", "## Review focus")
FILE_LIMIT = 150
BAD_CHARS = {"\u2014": "em dash", "\u2015": "horizontal bar", "\u201c": "curly quote", "\u201d": "curly quote",
             "\u2019": "curly apostrophe", "\u00a0": "no-break space", "\u202f": "narrow no-break space",
             "\u200b": "zero width space", "\ufeff": "byte order mark"}
FORBIDDEN = (
    (re.compile(r"git\s+add\s+(\.|-A|--all|-a|\*)(\s|$|`)"), "git add of a whole tree"),
    (re.compile(r"git\s+commit\b[^\n]*\s-[a-zA-Z]*a[a-zA-Z]*(\s|$)"), "git commit -a"),
    (re.compile(r"git\s+(push|pull|fetch|clone)\b"), "direct network git command"),
    (re.compile(r"--no-verify"), "--no-verify"),
    (re.compile(r"--amend"), "--amend"),
    (re.compile(r"co-authored-by|generated with|claude\.ai/code", re.IGNORECASE), "AI attribution"),
    (re.compile(r"\b(TBD|TODO|FIXME)\b"), "placeholder"),
    (re.compile(r"similar to task|add appropriate|handle edge cases|fill in details", re.IGNORECASE),
     "vague step"),
)


def check_text(text):
    problems = []
    for number, line in enumerate(text.splitlines(), 1):
        for pattern, label in FORBIDDEN:
            if pattern.search(line):
                problems.append(f"line {number}: {label}")
        for char, label in BAD_CHARS.items():
            if char in line:
                problems.append(f"line {number}: {label}")
    return problems


def check_header(header):
    problems = [f"header: missing '{name}: ...' line" for name in LABELS if name not in header_labels(header)]
    problems += [f"header: missing section '{title}'" for title in SECTIONS if title not in header]
    return problems


def _step_titles(steps):
    return [step["title"].lower() for step in steps]


def _check_order(label, body, files):
    steps = task_steps(body)
    if not steps:
        return [f"{label}: no '- [ ] Step N:' lines"]
    titles = _step_titles(steps)
    problems = []
    if not NO_TEST.search(body):
        if "test" not in titles[0] or len(titles) < 2 or "run" not in titles[1]:
            problems.append(f"{label}: step 1 writes the test and step 2 runs it")
        if not any(kind == "Test" for kind, _, _ in files):
            problems.append(f"{label}: no 'Test:' file and no 'No test:' reason")
    if "commit" not in titles[-1]:
        problems.append(f"{label}: the last step is the commit")
    return problems


def _check_commit(label, body, files):
    steps = task_steps(body)
    if not steps or "commit" not in steps[-1]["title"].lower():
        return []
    last = steps[-1]["title"] + steps[-1]["text"]
    paths = commit_paths(last)
    problems = []
    if "clean-commits" not in last:
        problems.append(f"{label}: the commit step does not go through clean-commits")
    if paths is None:
        return problems + [f"{label}: the commit step has no 'Paths: `a`, `b`' line"]
    expected = {path for _, path, _ in files}
    if paths != expected:
        problems.append(f"{label}: commit paths differ from Files, missing {sorted(expected - paths)}, "
                        f"extra {sorted(paths - expected)}")
    return problems


def _check_sizes(label, files):
    problems = []
    for kind, path, note in files:
        size = SIZE_NOTE.search(note)
        if size and int(size.group(1)) > FILE_LIMIT:
            problems.append(f"{label}: {path} is planned at {size.group(1)} lines, the limit is {FILE_LIMIT}")
    return problems


def check_task(task):
    label = f"task {task['number']}"
    files = task_files(task["body"])
    if not files:
        return [f"{label}: no Files list"]
    return _check_sizes(label, files) + _check_order(label, task["body"], files) + _check_commit(
        label, task["body"], files)
