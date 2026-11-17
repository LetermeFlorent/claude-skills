import os
import posixpath
import re
from collections import defaultdict

from extract import MIN_NAME
from langs import COMMON, EXT_LANG

MAX_DEF_FILES = 4
MAX_DROPS = 2
INDEX_NAMES = frozenset({"__init__", "index", "mod"})
RUST_ROOTS = re.compile(r"^(crate|self|super)/")
MODULE_SEPARATORS = re.compile(r"::|\\|\.")


def def_index(files):
    defs = defaultdict(list)
    for path, entry in files.items():
        for name, kind, line in entry["defs"]:
            defs[name].append((path, line, kind))
    return dict(defs)


def linkable(name, places):
    return len(name) >= MIN_NAME and name not in COMMON and len({p for p, _, _ in places}) <= MAX_DEF_FILES


def mention_index(files, defs):
    mentions = defaultdict(set)
    for path, entry in files.items():
        for token in entry["tokens"]:
            if token in defs:
                mentions[token].add(path)
    return mentions


def reference_map(defs, mentions):
    refs = {}
    for name, places in defs.items():
        if linkable(name, places):
            who = sorted(mentions.get(name, set()) - {p for p, _, _ in places})
            if who:
                refs[name] = who
    return refs


def strip_ext(path):
    base, ext = os.path.splitext(path)
    return base if ext.lower() in EXT_LANG else path


def target_of(source, spec):
    spec = spec.strip()
    folder = posixpath.dirname(source)
    if spec.startswith(("./", "../")):
        return strip_ext(posixpath.normpath(posixpath.join(folder, spec))), True
    if spec.startswith("."):
        dots = len(spec) - len(spec.lstrip("."))
        for _ in range(dots - 1):
            folder = posixpath.dirname(folder)
        rest = spec[dots:].replace(".", "/")
        return posixpath.normpath(posixpath.join(folder, rest)) if rest else folder, True
    if "/" in spec:
        return strip_ext(posixpath.normpath(spec)), False
    return RUST_ROOTS.sub("", MODULE_SEPARATORS.sub("/", spec)), False


def stems(path):
    base = os.path.splitext(path)[0]
    found = [base]
    if posixpath.basename(base) in INDEX_NAMES:
        found.append(posixpath.dirname(base))
    return [s for s in found if s]


def stem_index(paths):
    index = defaultdict(list)
    for path in paths:
        for stem in stems(path):
            index[stem.rsplit("/", 1)[-1]].append((stem, path))
    return index


def _closeness(source, path):
    return len(os.path.commonprefix([posixpath.dirname(source), posixpath.dirname(path)]))


def resolve(source, spec, index):
    target, relative = target_of(source, spec)
    attempts = [target]
    if not relative and "/" in target and "/" not in spec:
        attempts += [target.rsplit("/", i)[0] for i in range(1, MAX_DROPS + 1) if target.count("/") >= i]
    for attempt in attempts:
        found = [p for s, p in index.get(attempt.rsplit("/", 1)[-1], [])
                 if p != source and (s == attempt or (not relative and s.endswith("/" + attempt)))]
        if found:
            return min(found, key=lambda p: (-_closeness(source, p), len(p)))
    return None


def resolve_imports(files):
    index = stem_index(files)
    result = {}
    for path, entry in files.items():
        wanted = {resolve(path, spec, index) for spec in entry["imports"]}
        wanted.discard(None)
        if wanted:
            result[path] = sorted(wanted)
    return result


class Graph:
    def __init__(self, files):
        self.files = files
        self.defs = def_index(files)
        self.mentions = mention_index(files, self.defs)
        self.refs = reference_map(self.defs, self.mentions)
        self.imports = resolve_imports(files)
        self.importers = defaultdict(list)
        for source, targets in self.imports.items():
            for target in targets:
                self.importers[target].append(source)

    def symbol_count(self):
        return sum(len(places) for places in self.defs.values())

    def edge_count(self):
        return sum(len(v) for v in self.refs.values()) + sum(len(v) for v in self.imports.values())

    def uses(self, path):
        return sorted(name for name, who in self.refs.items() if path in who)

    def adjacency(self):
        adj = defaultdict(set)
        for source, targets in self.imports.items():
            adj[("f", source)].update(("f", t) for t in targets)
        for name, who in self.refs.items():
            for place, _, _ in self.defs[name]:
                symbol = ("s", place, name)
                adj[symbol].add(("f", place))
                for referrer in who:
                    adj[("f", referrer)].add(symbol)
        return adj
