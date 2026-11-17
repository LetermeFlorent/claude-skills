import ast
import re

from knowledge.docs import MARKDOWN, is_markdown, markdown_facts
from langs import KEYWORDS, OTHER, lang_of, rules_for

IDENT = re.compile(r"[A-Za-z_]\w*")
MIN_NAME = 3
MAX_LINE = 1000
NESTED_FIELDS = ("body", "orelse", "finalbody", "handlers")
FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)


def _scan(body, scope, facts):
    defs, imports = facts
    for node in body:
        if isinstance(node, FUNCTIONS):
            defs.append([node.name, "method" if scope == "class" else "function", node.lineno])
            _scan(node.body, "function", facts)
        elif isinstance(node, ast.ClassDef):
            defs.append([node.name, "class", node.lineno])
            _scan(node.body, "class", facts)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = "." * node.level + (node.module or "")
            imports.append(base)
            joiner = "" if base.endswith(".") else "."
            imports.extend(f"{base}{joiner}{alias.name}" for alias in node.names)
        elif isinstance(node, ast.Assign) and scope == "module":
            defs.extend([t.id, "const", node.lineno] for t in node.targets
                        if isinstance(t, ast.Name) and t.id.isupper())
        else:
            for field in NESTED_FIELDS:
                child = getattr(node, field, None)
                if isinstance(child, list):
                    _scan(child, scope, facts)


def python_facts(text):
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        return None
    facts = ([], [])
    _scan(tree.body, "module", facts)
    return facts


def regex_facts(rules, text):
    defs = []
    for number, line in enumerate(text.split("\n"), 1):
        if len(line) > MAX_LINE:
            continue
        for kind, pattern in rules["defs"]:
            found = pattern.match(line)
            if found and found.group(1) not in KEYWORDS:
                defs.append([found.group(1), kind, number])
                break
    imports = [m.group(1) for pattern in rules["imports"] for m in pattern.finditer(text)]
    return defs, imports


def tokens_of(text, defs):
    own = {}
    for name, _, line in defs:
        own.setdefault(line, set()).add(name)
    found = set()
    for number, line in enumerate(text.split("\n"), 1):
        skip = own.get(number, ())
        found.update(t for t in IDENT.findall(line) if len(t) >= MIN_NAME and t not in skip)
    return sorted(found)


def markdown_entry(text):
    defs, tokens = markdown_facts(text)
    found = sorted(t for t in tokens if len(t) >= MIN_NAME)
    return {"lang": MARKDOWN, "lines": text.count("\n") + 1, "defs": defs, "imports": [], "tokens": found}


def extract(path, text):
    if is_markdown(path):
        return markdown_entry(text)
    lang = lang_of(path)
    entry = {"lang": lang or OTHER, "lines": text.count("\n") + 1, "defs": [], "imports": [], "tokens": []}
    if lang is None:
        return entry
    facts = python_facts(text) if lang == "python" else regex_facts(rules_for(lang), text)
    if facts:
        entry["defs"], entry["imports"] = facts
    entry["tokens"] = tokens_of(text, entry["defs"])
    return entry
