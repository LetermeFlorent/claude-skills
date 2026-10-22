import re

HEADER = "# SDD ledger, plan: {plan}"
IDS = r"(\d+(?:,\d+)*)"
COMPLETE = re.compile(rf"^Task {IDS}: complete, commit ([0-9a-f]{{7,40}})\b", re.IGNORECASE)
ROUND = re.compile(rf"^Task {IDS}: fix round (\d+)/\d+", re.IGNORECASE)
FINAL_DONE = re.compile(r"^Final: complete\b", re.IGNORECASE)
NOTE = re.compile(rf"^(Task {IDS}|Final|Scan|Ruling|Note):\s+\S")
RULING = "Ruling:"
BANNED = {chr(0x2014): "em dash", chr(0x2013): "en dash", chr(0x201C): "curly quote",
          chr(0x201D): "curly quote", chr(0x2019): "curly apostrophe"}


def numbers(text):
    return [int(part) for part in text.split(",")]


def parse(lines):
    state = {"complete": {}, "rounds": {}, "rulings": [], "final": False}
    for raw in lines:
        line = raw.strip()
        done, fix = COMPLETE.match(line), ROUND.match(line)
        for number in numbers(done.group(1)) if done else []:
            state["complete"][number] = done.group(2)
        for number in numbers(fix.group(1)) if fix else []:
            state["rounds"][number] = int(fix.group(2))
        if RULING in line:
            state["rulings"].append(line)
        state["final"] = state["final"] or bool(FINAL_DONE.match(line))
    return state


def pending(plan_numbers, state):
    return [number for number in plan_numbers if number not in state["complete"]]


def note_problems(text):
    problems = [f"{name} in the note: use a comma, a colon or |" for char, name in BANNED.items() if char in text]
    if "\n" in text or "\r" in text:
        problems.append("one line per note")
    if not NOTE.match(text):
        problems.append("a note starts with 'Task <N>: ', 'Final: ', 'Scan: ', 'Ruling: ' or 'Note: '")
    return sorted(set(problems))
