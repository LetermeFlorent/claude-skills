import re

MARKDOWN = "markdown"
MARKDOWN_EXTS = (".md", ".markdown", ".mdx")
HEADING_KIND = "heading"
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
SPAN = re.compile(r"`([^`\n]+)`")
IDENT = re.compile(r"[A-Za-z_]\w*")
CODE_LIKE = re.compile(r"\b(?:[A-Za-z]\w*_\w+|_\w+|[a-z]+[A-Z]\w*|[A-Za-z_]\w*(?=\())")


def is_markdown(path):
    return path.lower().endswith(MARKDOWN_EXTS)


def markdown_facts(text):
    defs, tokens, fenced = [], set(), False
    for number, line in enumerate(text.split("\n"), 1):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            tokens.update(IDENT.findall(line))
            continue
        heading = HEADING.match(line)
        if heading:
            defs.append([heading.group(1), HEADING_KIND, number])
        for span in SPAN.findall(line):
            tokens.update(IDENT.findall(span))
        tokens.update(CODE_LIKE.findall(SPAN.sub(" ", line)))
    return defs, tokens
