import json
import os
import sys
import threading
from pathlib import Path

sys.dont_write_bytecode = True

SKILLS = ("terse-speech", "least-code")
SKILL_FILE = "SKILL.md"
FENCE = "---"
BOM = "\ufeff"
ENCODING = "utf-8"
STDIN_WAIT = 2
EVENT_KEY = "hook_event_name"
EMPTY = "{}"
EXIT_OK = 0


def strip_front_matter(text):
    lines = text.lstrip(BOM).splitlines()
    if lines and lines[0].strip() == FENCE:
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == FENCE:
                lines = lines[index + 1:]
                break
    return "\n".join(lines).strip()


def read_bodies(repo):
    bodies = []
    for name in SKILLS:
        try:
            text = (Path(repo) / name / SKILL_FILE).read_text(encoding=ENCODING)
        except OSError:
            continue
        body = strip_front_matter(text)
        if body:
            bodies.append(body)
    return bodies


def payload(repo, event):
    bodies = read_bodies(repo)
    if not bodies or not event:
        return {}
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": "\n\n".join(bodies)}}


def read_stdin():
    stream, box = sys.stdin, []
    if stream is None or stream.isatty():
        return ""

    def pull():
        try:
            box.append(stream.read())
        except (OSError, ValueError):
            pass

    worker = threading.Thread(target=pull, daemon=True)
    worker.start()
    worker.join(STDIN_WAIT)
    return box[0] if box else ""


def event_name(text, argv):
    try:
        data = json.loads(text)
        found = data.get(EVENT_KEY) if isinstance(data, dict) else None
    except ValueError:
        found = None
    return found if isinstance(found, str) and found else (argv[0] if argv else "")


def main(argv):
    repo = Path(__file__).resolve().parents[1]
    event = argv[0] if argv else event_name(read_stdin(), argv)
    print(json.dumps(payload(repo, event)))


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception:
        print(EMPTY)
    sys.stdout.flush()
    os._exit(EXIT_OK)
