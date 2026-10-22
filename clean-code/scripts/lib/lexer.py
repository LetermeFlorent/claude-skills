import re

DIRECTIVE = re.compile(r"eslint|@ts-|noqa|type:\s*ignore|pragma|pylint:|mypy:|go:build|go:generate|prettier-ignore|"
                       r"webpackChunkName|SAFETY:|istanbul ignore|c8 ignore|NOLINT|rubocop:|coding[:=]|SPDX|@license|"
                       r"@preserve|biome-ignore|deno-lint|swiftlint|ktlint|clippy|#region|#endregion|<reference ")
TRIPLE = ('"""', "'''")
TEMPLATE = "`"
ESCAPE_WIDTH = 2
QUOTES = (TEMPLATE, '"', "'")
DOC_LINES = ("///", "//!")
DOC_BLOCK, EMPTY_BLOCK = "/**", "/**/"
EMPTY_STRING = '""'
OPENERS, CLOSERS = "([{", ")]}"
BLOCK, LINE, STRING = "block", "line", "string"
C_STYLE = (("//",), (("/*", "*/"),))
LANGS = {
    **dict.fromkeys((".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".java", ".kt", ".kts", ".scala", ".groovy",
                     ".rs", ".go", ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".swift", ".dart", ".php", ".cl",
                     ".scss", ".less"), C_STYLE),
    ".css": ((), (("/*", "*/"),)),
    **dict.fromkeys((".vue", ".svelte", ".html"), (("//",), (("/*", "*/"), ("<!--", "-->")))),
    **dict.fromkeys((".py", ".rb", ".sh", ".bash", ".r", ".pl"), (("#",), ())),
    ".ps1": (("#",), (("<#", "#>"),)),
    **dict.fromkeys((".lua", ".luau"), (("--",), (("--[[", "]]"),))),
    ".sql": (("--",), (("/*", "*/"),)),
}
PYTHON_SUFFIX = ".py"
PROSE = {".md", ".mdx", ".txt", ".rst", ".adoc"}


def _string_end(line, start, quote):
    index = start
    while index < len(line):
        if line[index] == "\\":
            index += ESCAPE_WIDTH
            continue
        if line.startswith(quote, index):
            return index
        index += 1
    return -1


class _Scanner:
    def __init__(self, style, python):
        self.line_tokens, self.blocks = style
        self.quotes = (TRIPLE if python else ()) + QUOTES
        self.python, self.state = python, None

    def _opener(self, line, index):
        for opener, closer in self.blocks:
            if line.startswith(opener, index):
                return BLOCK, opener, closer
        for token in self.line_tokens:
            if line.startswith(token, index):
                return LINE, token, ""
        for quote in self.quotes:
            if line.startswith(quote, index):
                return STRING, quote, quote
        return None

    def _inside(self, line, index, row):
        kind, closer, quiet = self.state
        end = line.find(closer, index) if kind == BLOCK else _string_end(line, index, closer)
        piece = line[index:] if end < 0 else line[index:end]
        if kind == BLOCK or quiet:
            row["comment"] += piece or " "
            row["doc"] = row["doc"] or quiet
        else:
            row["strings"].append(piece)
        if end < 0:
            return None
        self.state = None
        row["code"] += EMPTY_STRING if kind == STRING else ""
        return end + len(closer)

    def _start(self, line, index, row):
        found = self._opener(line, index)
        if not found:
            row["code"] += line[index]
            return index + 1
        kind, token, closer = found
        if kind == LINE:
            row["comment"] += line[index + len(token):] or " "
            row["doc"] = row["doc"] or line.startswith(DOC_LINES, index)
            return None
        if kind == BLOCK:
            self.state = (BLOCK, closer, line.startswith(DOC_BLOCK, index) and not line.startswith(EMPTY_BLOCK, index))
            return index + len(token)
        if token in TRIPLE or token == TEMPLATE:
            self.state = (STRING, token, self.python and token in TRIPLE and not row["code"].strip())
            return index + len(token)
        end = _string_end(line, index + 1, token)
        row["strings"].append(line[index + 1:] if end < 0 else line[index + 1:end])
        row["code"] += EMPTY_STRING
        return len(line) if end < 0 else end + 1

    def row(self, line):
        row = {"code": "", "comment": "", "doc": False, "strings": []}
        index = 0
        while index is not None and index < len(line):
            index = self._inside(line, index, row) if self.state else self._start(line, index, row)
        return row


def scan(lines, style, python=False):
    scanner = _Scanner(style, python)
    return [scanner.row(line) for line in lines]


def balance(code):
    return sum(code.count(char) for char in OPENERS) - sum(code.count(char) for char in CLOSERS)


def is_directive(text):
    return bool(DIRECTIVE.search(text))
