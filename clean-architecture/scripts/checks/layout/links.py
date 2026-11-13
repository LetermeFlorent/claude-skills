from collections import defaultdict
from pathlib import PurePosixPath

from imports import parse, resolve
from lexer import PYTHON_SUFFIX

MISPLACED_RULE = 2
CYCLE_RULE = 5
PACKAGE_INIT = "__init__.py"


def folder(rel):
    return str(PurePosixPath(rel).parent)


def related(first, second):
    return first == second or first == "." or second == "." or first.startswith(second + "/") or \
        second.startswith(first + "/")


def edges(files):
    index = {item["rel"]: item for item in files}
    for item in files:
        if not item["code"] or item["data"]:
            continue
        for number, source, names in parse(item):
            targets = {resolve(item, source, index)}
            if item["path"].suffix == PYTHON_SUFFIX:
                joiner = "" if source.endswith(".") else "."
                targets |= {resolve(item, f"{source}{joiner}{name}", index) for name, _ in names}
            for target in targets - {None, item["rel"]}:
                yield item, number, target


def misplaced(files, links):
    users = defaultdict(set)
    for item, _, target in links:
        if not item["test"]:
            users[target].add(folder(item["rel"]))
    findings = []
    for item in files:
        home, used_in = folder(item["rel"]), users.get(item["rel"], set())
        if item["test"] or PurePosixPath(item["rel"]).name == PACKAGE_INIT or len(used_in) != 1:
            continue
        (other,) = used_in
        if not related(home, other):
            findings.append({"rule": MISPLACED_RULE, "file": item["rel"], "line": 1,
                             "what": f"used only from {other}/, lives in {home}/",
                             "proof": f"every non-test import of it is in {other}/"})
    return findings


def components(graph):
    order, low, stack, found, counter = {}, {}, [], [], [0]

    def visit(node):
        order[node] = low[node] = counter[0]
        counter[0] += 1
        stack.append(node)
        for nxt in sorted(graph[node]):
            if nxt not in order:
                visit(nxt)
                low[node] = min(low[node], low[nxt])
            elif nxt in stack:
                low[node] = min(low[node], order[nxt])
        if low[node] == order[node]:
            group = []
            while not group or group[-1] != node:
                group.append(stack.pop())
            found.append(sorted(group))

    for node in sorted(graph):
        if node not in order:
            visit(node)
    return [group for group in found if len(group) > 1]


def cycles(links):
    graph, lines = defaultdict(set), defaultdict(list)
    for item, number, target in links:
        start, end = folder(item["rel"]), folder(target)
        if not related(start, end) and not item["test"]:
            graph[start].add(end)
            graph.setdefault(end, set())
            lines[(start, end)].append(f"{item['rel']}:{number}")
    findings = []
    for group in components(graph):
        proof = [lines[(a, b)][0] for a in group for b in group if lines.get((a, b))]
        findings.append({"rule": CYCLE_RULE, "file": group[0], "line": 0,
                         "what": f"import cycle between folders {', '.join(group)}", "proof": ", ".join(proof)})
    return findings


def check(files, root, config):
    links = list(edges(files))
    return misplaced(files, links) + cycles(links), {}
