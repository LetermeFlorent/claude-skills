import difflib
import re
from collections import deque

CAMEL_LOW_UP = re.compile(r"([a-z0-9])([A-Z])")
CAMEL_ACRONYM = re.compile(r"([A-Z]+)([A-Z][a-z])")
WORD = re.compile(r"[A-Za-z0-9]+")
EXACT_POINTS = 4
PREFIX_POINTS = 3
SUBSTRING_POINTS = 2
PATH_POINTS = 1
ALL_WORDS_BONUS = 3
CLOSE_CUTOFF = 0.6


def words(text):
    spaced = CAMEL_ACRONYM.sub(r"\1 \2", CAMEL_LOW_UP.sub(r"\1 \2", text))
    return [w.lower() for w in WORD.findall(spaced)]


def score(query, name, path):
    name_words, path_words, lowered = words(name), words(path), name.lower()
    total, hits = 0, 0
    for word in query:
        if word in name_words:
            points = EXACT_POINTS
        elif any(w.startswith(word) for w in name_words):
            points = PREFIX_POINTS
        elif word in lowered:
            points = SUBSTRING_POINTS
        elif word in path_words or word in path.lower():
            points = PATH_POINTS
        else:
            points = 0
        total += points
        hits += bool(points)
    return total + (ALL_WORDS_BONUS if hits == len(query) else 0) if total else 0


def closest(query, names, count):
    return difflib.get_close_matches(query, names, n=count, cutoff=CLOSE_CUTOFF)


def components(adj):
    index, low, stack, on_stack, result = {}, {}, [], set(), []
    for start in adj:
        if start in index:
            continue
        index[start] = low[start] = len(index)
        stack.append(start)
        on_stack.add(start)
        work = [(start, iter(adj.get(start, ())))]
        while work:
            node, neighbours = work[-1]
            descended = False
            for nxt in neighbours:
                if nxt not in index:
                    index[nxt] = low[nxt] = len(index)
                    stack.append(nxt)
                    on_stack.add(nxt)
                    work.append((nxt, iter(adj.get(nxt, ()))))
                    descended = True
                    break
                if nxt in on_stack:
                    low[node] = min(low[node], index[nxt])
            if descended:
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[node])
            if low[node] == index[node]:
                result.append(_pop_component(stack, on_stack, node))
    return [sorted(c) for c in result if len(c) > 1]


def _pop_component(stack, on_stack, node):
    members = []
    while True:
        member = stack.pop()
        on_stack.discard(member)
        members.append(member)
        if member == node:
            return members


def shortest_path(adj, starts, goals):
    parent = {s: None for s in starts}
    queue = deque(starts)
    while queue:
        node = queue.popleft()
        if node in goals:
            chain = []
            while node is not None:
                chain.append(node)
                node = parent[node]
            return chain[::-1]
        for nxt in sorted(adj.get(node, ()), key=str):
            if nxt not in parent:
                parent[nxt] = node
                queue.append(nxt)
    return None
