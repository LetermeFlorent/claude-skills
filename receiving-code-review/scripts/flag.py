import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from points import split_points
from rules import looks_vague, match_rules

TOOL = "receiving-code-review"
ENCODING = "utf-8"
FAILED, REFUSED = 1, 2
SHOWN = 90


def _read(argument):
    if argument == "-":
        return sys.stdin.read()
    return Path(argument).read_text(encoding=ENCODING, errors="replace")


def _row(index, line, text):
    flags = match_rules(text)
    vague = ["unclear"] if looks_vague(text) else []
    names = [name for name, _ in flags] + vague
    head = text if len(text) <= SHOWN else text[:SHOWN] + "..."
    print(f"point {index} (line {line}): {head}")
    for name, advice in flags:
        print(f"  {name}: {advice}")
    if vague:
        print("  unclear: short and no file, line or name; ask before touching code")
    return bool(names)


def main():
    if len(sys.argv) != 2:
        print(f"{TOOL}: usage: python -I flag.py <review file or ->")
        sys.exit(REFUSED)
    points = split_points(_read(sys.argv[1]))
    if not points:
        print(f"{TOOL}: the feedback holds no point")
        sys.exit(REFUSED)
    flagged = sum(_row(*point) for point in points)
    print(f"points: {len(points)}, flagged: {flagged}")
    print("flags are hints from patterns; every point is still checked against the code")


try:
    main()
except SystemExit:
    raise
except Exception as error:
    print(f"{TOOL}: {type(error).__name__}: {error}")
    print('by hand: read the feedback and mark each point right, wrong, unclear or forbidden')
    sys.exit(FAILED)
