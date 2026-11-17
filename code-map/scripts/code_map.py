import argparse
import sys
import time
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))
sys.path.insert(0, str(HERE))

import queries
import report
from common import TOOL, guard
from store import find_root, refresh
from graph import Graph


def parser():
    top = argparse.ArgumentParser(prog=TOOL, description="Map of a project's code: definitions, imports, references.")
    sub = top.add_subparsers(dest="command", required=True)

    def add(name, text):
        item = sub.add_parser(name, help=text, description=text)
        item.add_argument("--root", help="project folder (default: git top level, else current folder)")
        return item

    add("build", "force a refresh and print counts").add_argument("--scope", default="", help="map only this subfolder")
    add("report", "write report.md: biggest files, hubs, cycles, folders, dead code")
    finder = add("find", "symbols and files matching words")
    finder.add_argument("words", nargs="+")
    finder.add_argument("--budget", type=int, default=queries.DEFAULT_BUDGET, help="output size in characters")
    add("explain", "where a symbol or file is defined and used").add_argument("name")
    way = add("path", "shortest chain of references and imports")
    way.add_argument("source")
    way.add_argument("target")
    add("unused", "dead code candidates")
    return top.parse_args()


def summary(graph, changed, started):
    langs = Counter(e["lang"] for e in graph.files.values())
    shown = " ".join(f"{name} {count}" for name, count in langs.most_common())
    return [f"files {len(graph.files)}, symbols {graph.symbol_count()}, edges {graph.edge_count()}",
            f"languages: {shown or 'none'}",
            f"read {changed} changed files in {time.monotonic() - started:.1f} s"]


def main():
    args = parser()
    started = time.monotonic()
    root = find_root(args.root)
    data, changed = refresh(root, args.scope if args.command == "build" else None)
    graph = Graph(data["files"])
    if args.command == "build":
        lines = summary(graph, changed, started)
    elif args.command == "report":
        lines = report.report(graph, root)
    elif args.command == "find":
        lines = queries.find(graph, args.words, args.budget)
    elif args.command == "explain":
        lines = queries.explain(graph, args.name)
    elif args.command == "path":
        lines = queries.path_between(graph, args.source, args.target)
    else:
        lines = queries.unused(graph)
    print("\n".join(lines))


if __name__ == "__main__":
    guard(main, f'python -I "{Path(__file__).resolve().as_posix()}" --help')
