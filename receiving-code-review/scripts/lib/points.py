import re

START = re.compile(r"^\s*(?:(\d+)[.)]|[-*+])\s+(?=\S)")
PREAMBLE = 0


def _starts_point(line):
    return START.match(line) is not None


def _split_marked(lines):
    points, current, label = [], None, 0
    for number, line in enumerate(lines, 1):
        found = START.match(line)
        if found:
            label = int(found.group(1)) if found.group(1) else label + 1
            current = [number, [START.sub("", line).strip()], label]
            points.append(current)
        elif current is not None and line.strip():
            current[1].append(line.strip())
        elif current is None and line.strip():
            current = [number, [line.strip()], PREAMBLE]
            points.append(current)
    return points


def _split_paragraphs(lines):
    points, current = [], None
    for number, line in enumerate(lines, 1):
        if not line.strip():
            current = None
        elif current is None:
            current = [number, [line.strip()], len(points) + 1]
            points.append(current)
        else:
            current[1].append(line.strip())
    return points


def split_points(text):
    lines = text.splitlines()
    marked = any(_starts_point(line) for line in lines)
    raw = _split_marked(lines) if marked else _split_paragraphs(lines)
    return [(label, line, " ".join(parts)) for line, parts, label in raw]
