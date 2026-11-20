import argparse
import sys
sys.dont_write_bytecode = True
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from blender import blender_or_refuse, guard, refuse
from docsite import base_url, find_lines, index, page_text, search, version

HINT = "open https://docs.blender.org/manual/en/<x.y>/ and use its search box"
SHOWN = 15


def parse(argv):
    parser = argparse.ArgumentParser(description="Search the Blender docs of the installed version, read one page.")
    parser.add_argument("action", choices=("search", "page"))
    parser.add_argument("what", help="search: words; page: URL or path such as modeling/modifiers/index.html")
    parser.add_argument("--docs", choices=("manual", "api"), default="manual")
    parser.add_argument("--find", default="", help="page: print only the lines around this word")
    parser.add_argument("--version", default="", help="x.y; default: the installed Blender")
    return parser.parse_args(argv)


def main():
    options = parse(sys.argv[1:])
    release = options.version or version(blender_or_refuse())
    if not release:
        refuse(["could not read the Blender version: pass --version x.y"])
    root = base_url(options.docs, release)
    if options.action == "search":
        hits = search(index(root), options.what)
        print(f"{options.docs} {release}: {len(hits)} pages match '{options.what}'")
        for score, title, path in hits[:SHOWN]:
            print(f"  {root}{path} | {title}")
        return
    url = options.what if options.what.startswith("http") else root + options.what.lstrip("/")
    text = page_text(url)
    lines = find_lines(text, options.find) if options.find else text.splitlines()
    print(url)
    print("\n".join(lines) if lines else f"'{options.find}' not on this page")


if __name__ == "__main__":
    guard(main, HINT)
