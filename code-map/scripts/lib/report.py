from collections import Counter

from algo import components
from queries import unused
from store import REPORT_NAME, store_dir

TOP = 10
TOP_FOLDERS = 15
CYCLE_SHOWN = 6
ROOT_FOLDER = "."


def sections(graph):
    files = graph.files
    biggest = sorted(files, key=lambda p: (-files[p]["lines"], p))[:TOP]
    hubs = sorted(graph.refs, key=lambda n: (-len(graph.refs[n]), n))[:TOP]
    folders = Counter(p.split("/")[0] if "/" in p else ROOT_FOLDER for p in files)
    cycles = components({k: v for k, v in graph.imports.items()})
    dead = unused(graph)
    out = ["## Biggest files"]
    out += [f"{p} {files[p]['lines']} lines" for p in biggest]
    out += ["## Hubs (most referencing files)"]
    out += [f"{n} {graph.defs[n][0][0]}:{graph.defs[n][0][1]} <- {len(graph.refs[n])} files" for n in hubs]
    out += [f"## Import cycles ({len(cycles)})"]
    out += [" , ".join(c[:CYCLE_SHOWN]) + (f" +{len(c) - CYCLE_SHOWN}" if len(c) > CYCLE_SHOWN else "")
            for c in cycles[:TOP]]
    out += ["## Folders"]
    out += [f"{name} {count} files" for name, count in folders.most_common(TOP_FOLDERS)]
    out += [f"## Dead code candidates ({len(dead) - 1})"]
    out += dead[:TOP]
    return out


def report(graph, root):
    lines = sections(graph)
    lines.append(f"{len(graph.files)} files, {graph.symbol_count()} symbols, {graph.edge_count()} edges")
    folder = store_dir(root)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / REPORT_NAME).write_text("# Code map report\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
    return lines
