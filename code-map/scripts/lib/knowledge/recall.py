from algo import score, words
from knowledge import notes
from knowledge.docs import MARKDOWN
from queries import NO_MATCH, explain, find, names_of, resolve_file, SHOWN_ITEMS


def files_of(graph, text):
    return resolve_file(graph, text) or sorted({path for path, _, _ in graph.defs.get(text, [])})


def docs_about(graph, name):
    return sorted(p for p in graph.mentions.get(name, ()) if graph.files[p]["lang"] == MARKDOWN)


def find_notes(items, query):
    query_words = [w for text in query for w in words(text)]
    scored = [(-score(query_words, n["text"], " ".join(n.get("about", []))), n["id"], n) for n in items]
    return [n for points, _, n in sorted(scored, key=lambda s: s[:2]) if points]


def notes_for(graph, items, name):
    paths = resolve_file(graph, name)
    return [n for n in items if name in n.get("about", [])
            or any(p in n.get("about", []) or p in n.get("hashes", {}) for p in paths)]


def shown(root, items):
    return [notes.line(n, notes.is_stale(root, n)) for n in items]


def find_all(graph, root, query, budget):
    lines = shown(root, find_notes(notes.load(root)["notes"], query))
    code = find(graph, query, budget)
    if lines and code[0].startswith(NO_MATCH):
        return lines + [f"{len(lines)} notes, no symbol or file match"]
    return lines + code


def explain_all(graph, root, name):
    lines = explain(graph, name)
    docs = docs_about(graph, name)
    if docs:
        lines.append(f"docs: {names_of(docs, SHOWN_ITEMS)}")
    return lines + shown(root, notes_for(graph, notes.load(root)["notes"], name))
