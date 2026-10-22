FENCE = "---"
QUOTES = "\"'"
BLOCK_MARKERS = (">", "|", ">-", "|-", ">+", "|+")


def _unquote(value):
    if len(value) > 1 and value[0] == value[-1] and value[0] in QUOTES:
        return value[1:-1]
    return value


def parse_fields(lines):
    fields, last = {}, None
    for line in lines:
        key, separator, value = line.partition(":")
        if separator and key.strip() and not line[:1].isspace():
            last = key.strip()
            value = value.strip()
            fields[last] = "" if value in BLOCK_MARKERS else _unquote(value)
        elif last and line.strip():
            fields[last] = (fields[last] + " " + line.strip()).strip()
    return fields


def split(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != FENCE:
        return None, lines, 0
    for index in range(1, len(lines)):
        if lines[index].strip() == FENCE:
            return parse_fields(lines[1:index]), lines[index + 1:], index + 1
    return None, lines, 0


def line_of(text, key):
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith(f"{key}:"):
            return number
    return 1
