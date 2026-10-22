import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from common import REFUSED, guard, read_text, show
from companions import check_commands, check_readme
from links import check_links
from pyrules import check_python
from skillmd import FILE, check_skill_md, command_names, owned_paths

HINT = 'python -I "<skill>/scripts/check_skill.py" "<skill folder>" [--draft]'
SCAN = 'next: python -I "<anti-empreinte>/scripts/scan.py" "{}" --no-git'


def arguments():
    parser = argparse.ArgumentParser(description="Check a skill folder against the format of this repository.")
    parser.add_argument("folder", help="the skill folder, the one that holds SKILL.md")
    parser.add_argument("--draft", action="store_true", help="before the tests: the tested section must not exist yet")
    return parser.parse_args()


def findings(folder, draft):
    commands = command_names(folder)
    found = check_skill_md(folder, commands)
    found += check_links(folder, read_text(folder / FILE) or "", owned_paths(folder))
    found += check_readme(folder, draft)
    found += check_commands(folder, folder.name)
    return found + check_python(folder)


def main():
    options = arguments()
    folder = Path(options.folder).resolve()
    if not (folder / FILE).is_file():
        print(f"refused: no {FILE} in {folder}")
        sys.exit(REFUSED)
    refused = show(findings(folder, options.draft))
    print(SCAN.format(folder.as_posix()))
    if refused:
        sys.exit(REFUSED)


if __name__ == "__main__":
    guard(main, HINT)
