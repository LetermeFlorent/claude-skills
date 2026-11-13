import argparse
import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from common import compact, guard, refuse
from files import is_page, kind_of, read_text, relative, scanned, write_text
from gitlog import find_root, findings
from markdown import drop_separators, nested_fences, prose_lines, quoted, separators, structure
from metadata import document, image
from signatures import AI_FILES, LEFTOVER_FILES
from text import clean, fix_line, in_value, line_markers, outside_code, safe_markers
from patterns import SIGNATURE, UI_DEFAULT

STATUSES = FIXED, HAND, FLAG = ("fixed", "by hand", "flag")
STRUCTURAL = ("stock readme outline", "table of contents on a short page")
IN_CODE = " (a string stays, a comment is fixed)"
LINE_ENDINGS = "\r\n"


class Report:
    def __init__(self, base, git):
        self.base, self.git, self.rows = base, git, []

    def add(self, path, status, kind, lines=None):
        rel = relative(path, self.base)
        where = rel + (f":{lines[0]}" if lines else "")
        detail = f" (lines {compact(lines)})" if lines and len(lines) > 1 else ""
        self.rows.append(((STATUSES.index(status), rel, lines[0] if lines else 0), f"{where} {status}: {kind}{detail}"))

    def grouped(self, path, status, found):
        for kind, lines in sorted(found.items()):
            self.add(path, status, kind, sorted(set(lines)))

    def show(self):
        for _, row in sorted(self.rows):
            print(row)
        counts = [sum(1 for key, _ in self.rows if key[0] == rank) for rank in range(len(STATUSES))]
        print("{} fixed, {} to fix by hand, {} flagged".format(*counts))


def _prose(path, text, report, fix):
    raw = text.splitlines(keepends=True)
    lines = [line.rstrip(LINE_ENDINGS) for line in raw]
    hand, fixed, skipped = structure(lines), {}, quoted(lines)
    for number, line in prose_lines(lines):
        if number in skipped:
            continue
        for kind in line_markers(clean(outside_code(line)), True):
            hand.setdefault(kind, []).append(number)
        if fix:
            cleaned, kinds = fix_line(line)
            raw[number - 1] = cleaned + raw[number - 1][len(line):]
            for kind in kinds:
                fixed.setdefault(kind, []).append(number)
        else:
            for kind in safe_markers(outside_code(line)):
                hand.setdefault(kind, []).append(number)
    rules, nested = separators(lines), nested_fences(lines)
    if nested:
        hand["nested fence closed too short"] = nested
    if rules and fix:
        raw = drop_separators(raw, rules)
        fixed["separator line"] = rules
    elif rules:
        hand["separator line"] = rules
    if fix and fixed:
        write_text(path, "".join(raw))
    report.grouped(path, FIXED, fixed)
    report.grouped(path, FLAG, {kind: hand.pop(kind) for kind in STRUCTURAL if kind in hand})
    report.grouped(path, HAND, hand)


def _code(path, kind, text, report):
    hand, values = {}, {}
    ui = is_page(path) or kind == "style"
    for number, line in enumerate(text.splitlines(), 1):
        for kind in line_markers(line, False) + safe_markers(line):
            (values if in_value(kind, line) else hand).setdefault(kind, []).append(number)
        if ui and UI_DEFAULT.search(line):
            hand.setdefault("ui default nobody chose", []).append(number)
    report.grouped(path, HAND, hand)
    report.grouped(path, FLAG, {kind + IN_CODE: lines for kind, lines in values.items()})


def _value(path, text, report):
    signed = [number for number, line in enumerate(text.splitlines(), 1) if SIGNATURE.search(line)]
    if signed:
        report.add(path, FLAG, "attribution inside a value file", signed)


def scan_file(path, report, fix, anchor):
    kind = kind_of(Path(relative(path, anchor)))
    if LEFTOVER_FILES.search(path.name):
        report.add(path, FLAG, "agent leftover file")
    if not report.git and AI_FILES.search(relative(path, anchor)):
        report.add(path, FLAG, "AI tool config file")
    if kind in ("document", "image"):
        for finding in (document(path) if kind == "document" else image(path)):
            report.add(path, FLAG, finding)
        return
    text = read_text(path)
    if text is None:
        return
    if kind == "prose":
        _prose(path, text, report, fix)
    elif kind == "value":
        _value(path, text, report)
    else:
        _code(path, kind, text, report)


def scan_git(root, report):
    hand, flags = findings(root)
    for path, kind in hand:
        report.add(path, HAND, kind)
    for path, kind in flags:
        report.add(path, FLAG, kind)


def main():
    parser = argparse.ArgumentParser(description="Find, and with --fix remove, the traces of AI generation.")
    parser.add_argument("targets", nargs="*", default=["."], help="files or folders")
    parser.add_argument("--fix", action="store_true", help="apply the safe fixes to prose files")
    parser.add_argument("--no-git", action="store_true", help="skip the git history")
    args = parser.parse_args()
    targets = [Path(target).resolve() for target in args.targets]
    missing = [f"{target} does not exist" for target in targets if not target.exists()]
    if missing:
        refuse(missing)
    first = targets[0]
    root = find_root(first)
    report = Report(root or (first if first.is_dir() else first.parent), root is not None)
    for path, anchor in scanned(targets):
        scan_file(path, report, args.fix, anchor)
    if not args.no_git:
        for top in sorted({find_root(target) for target in targets} - {None}):
            scan_git(top, report)
    report.show()


if __name__ == "__main__":
    guard(main, "read the files by hand with the lists of reference/, and run git log --all for the trailers")
