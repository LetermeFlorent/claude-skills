import os
import re

from algo import closest, score, shortest_path, words
from extract import MIN_NAME

DEFAULT_BUDGET = 6000
SHOWN_REFS = 3
SHOWN_ITEMS = 15
CLOSE_COUNT = 5
MAX_UNUSED = 200
ENTRY_NAMES = frozenset({"main", "setup", "teardown", "setUp", "tearDown", "run", "init", "constructor", "new"})
DUNDER = re.compile(r"^__\w+__$")
TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|spec)/|(^|/)test_[^/]*$|[._](test|spec)\.[^/]*$")
INDEX_FILES = frozenset({"__init__", "index", "mod"})


def names_of(places, limit=SHOWN_REFS):
    shown = ", ".join(places[:limit])
    return shown + (f" +{len(places) - limit}" if len(places) > limit else "")


def candidates(graph):
    for name, places in graph.defs.items():
        for path, line, kind in places:
            yield path, line, kind, name
    for path in graph.files:
        yield path, 1, "file", os.path.basename(path)


def find(graph, query, budget):
    query_words = [w for text in query for w in words(text)]
    scored = []
    for path, line, kind, name in candidates(graph):
        points = score(query_words, name, path)
        if points:
            who = graph.importers.get(path, []) if kind == "file" else graph.refs.get(name, [])
            scored.append((-points, -len(who), path, line, kind, name, who))
    scored.sort()
    if not scored:
        pool = sorted(set(graph.defs) | {os.path.basename(p) for p in graph.files})
        near = [c for q in query for c in closest(q, pool, CLOSE_COUNT)]
        return [f"no match: {' '.join(query)}", "closest: " + (", ".join(dict.fromkeys(near)) or "none")]
    lines, used = [], 0
    for _, _, path, line, kind, name, who in scored:
        text = f"{path}:{line} {kind} {name}" + (f"  <- {names_of(who)}" if who else "")
        if used + len(text) > budget and lines:
            break
        lines.append(text)
        used += len(text) + 1
    lines.append(f"{len(lines)} shown of {len(scored)} matches")
    return lines


def resolve_file(graph, text):
    if text in graph.files:
        return [text]
    return [p for p in graph.files if p.endswith("/" + text)]


def explain_file(graph, path):
    lines = [f"file {path} ({graph.files[path]['lang']}, {graph.files[path]['lines']} lines)"]
    for name, kind, line in graph.files[path]["defs"][:SHOWN_ITEMS]:
        lines.append(f"  {path}:{line} {kind} {name}")
    lines.append("imports: " + (names_of(graph.imports.get(path, []), SHOWN_ITEMS) or "none"))
    lines.append("imported by: " + (names_of(graph.importers.get(path, []), SHOWN_ITEMS) or "none"))
    lines.append("uses: " + (names_of(graph.uses(path), SHOWN_ITEMS) or "none"))
    return lines


def explain(graph, name):
    places = graph.defs.get(name)
    if not places:
        paths = resolve_file(graph, name)
        if paths:
            return [line for path in paths for line in explain_file(graph, path)]
        pool = sorted(graph.defs)
        return [f"no match: {name}", "closest: " + (", ".join(closest(name, pool, CLOSE_COUNT)) or "none")]
    lines = []
    for path, line, kind in places:
        lines.append(f"defined {path}:{line} {kind} {name}")
        if name in graph.files[path]["tokens"]:
            lines.append("  also used inside its own file")
        lines.append(f"  file uses: {names_of(graph.uses(path), SHOWN_ITEMS) or 'none'}")
        lines.append(f"  file imports: {names_of(graph.imports.get(path, []), SHOWN_ITEMS) or 'none'}")
        lines.append(f"  file imported by: {names_of(graph.importers.get(path, []), SHOWN_ITEMS) or 'none'}")
    who = graph.refs.get(name, [])
    lines.append(f"referenced by: {names_of(who, SHOWN_ITEMS) or 'none'}")
    lines.append(f"{len(places)} definitions, {len(who)} referencing files")
    return lines


def nodes_for(graph, text):
    paths = resolve_file(graph, text)
    if paths:
        return [("f", p) for p in paths]
    return [("s", p, text) for p, _, _ in graph.defs.get(text, [])]


def describe(graph, node):
    if node[0] == "f":
        return f"file {node[1]}"
    line = next(l for p, l, _ in graph.defs[node[2]] if p == node[1])
    return f"symbol {node[1]}:{line} {node[2]}"


def path_between(graph, source, target):
    starts, goals = nodes_for(graph, source), nodes_for(graph, target)
    if not starts or not goals:
        missing = source if not starts else target
        return [f"no match: {missing}"]
    adj = graph.adjacency()
    chain, note = shortest_path(adj, starts, set(goals)), ""
    if chain is None:
        chain, note = shortest_path(adj, goals, set(starts)), " (reverse direction)"
    if chain is None:
        return [f"no path: {source} -> {target}"]
    return [describe(graph, n) for n in chain] + [f"{len(chain) - 1} hops{note}"]


def is_exempt(path, name):
    exempt = name in ENTRY_NAMES or DUNDER.match(name)
    stem = os.path.splitext(os.path.basename(path))[0]
    return bool(exempt or TEST_PATH.search(path) or stem in INDEX_FILES or name.startswith("test"))


def unused(graph):
    found = []
    for name, places in graph.defs.items():
        if len(name) < MIN_NAME or graph.mentions.get(name):
            continue
        found.extend((p, l, k, name) for p, l, k in places if not is_exempt(p, name))
    found.sort()
    lines = [f"{p}:{l} {k} {n}" for p, l, k, n in found[:MAX_UNUSED]]
    return lines + [f"{len(found)} dead code candidates ({len(lines)} shown)"]
