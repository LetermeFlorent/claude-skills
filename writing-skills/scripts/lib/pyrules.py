import ast
import io
import re
import tokenize

from common import CHECK, NOTE, REFUSE, read_text, relative

FILE_LINES, LINE_WIDTH, FUNCTION_LINES, PARAMETERS, FILES_PER_FOLDER = 150, 120, 40, 4, 8
FOREIGN = (".sh", ".js", ".cjs", ".mjs", ".ps1", ".dot", ".ts")
ALLOWED_COMMENT = re.compile(r"^#(!|\s*-\*-|\s*(noqa|type:|pragma|pylint|fmt:))")
BYTECODE_FLAG = "dont_write_bytecode"
GUARD_MARKS = ("guard(", "except Exception")
UNIT_TEST = "tests/test_pure.py"
CACHE, SCRIPTS = "__pycache__", "scripts/"
FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)


def comment_lines(text):
    found = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.COMMENT and not ALLOWED_COMMENT.match(token.string):
                found.append(token.start[0])
    except (tokenize.TokenError, SyntaxError):
        return found
    return found


def _parameters(node):
    named = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
    count = len(named) - (1 if named and named[0].arg in ("self", "cls") else 0)
    return count + (node.args.vararg is not None) + (node.args.kwarg is not None)


def function_findings(where, tree):
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, FUNCTIONS):
            continue
        length = node.end_lineno - node.lineno + 1
        if length > FUNCTION_LINES:
            found.append((REFUSE, where, node.lineno, f"{node.name} has {length} lines, {FUNCTION_LINES} at most"))
        if _parameters(node) > PARAMETERS:
            found.append((REFUSE, where, node.lineno, f"{node.name} takes {_parameters(node)} parameters"))
    return found


def source_findings(where, text):
    lines = text.splitlines()
    found = []
    if len(lines) > FILE_LINES:
        found.append((REFUSE, where, 0, f"{len(lines)} lines, {FILE_LINES} at most"))
    found += [(REFUSE, where, number, f"{len(line)} characters, {LINE_WIDTH} at most")
              for number, line in enumerate(lines, 1) if len(line) > LINE_WIDTH]
    found += [(REFUSE, where, number, "a comment: the code says it, or the name does")
              for number in comment_lines(text)]
    try:
        tree = ast.parse(text)
    except SyntaxError as error:
        return found + [(REFUSE, where, error.lineno or 0, f"does not parse: {error.msg}")]
    return found + function_findings(where, tree)


def _local_import_line(tree, local_names):
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] in local_names:
            lines.append(node.lineno)
        elif isinstance(node, ast.Import) and any(alias.name.split(".")[0] in local_names for alias in node.names):
            lines.append(node.lineno)
    return min(lines) if lines else None


def entry_findings(where, text, local_names):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    found, first = [], _local_import_line(tree, local_names)
    flag = next((number for number, line in enumerate(text.splitlines(), 1) if BYTECODE_FLAG in line), None)
    if first is not None and (flag is None or flag > first):
        found.append((REFUSE, where, first, f"a local import before sys.{BYTECODE_FLAG} = True"))
    if not any(mark in text for mark in GUARD_MARKS):
        found.append((CHECK, where, 0, "no guard around main: a crash would print a traceback"))
    return found


def _layout(folder, files):
    found = [(REFUSE, relative(path, folder), 0, f"a {CACHE} folder: delete it")
             for path in folder.rglob(CACHE) if path.is_dir()]
    found += [(NOTE, relative(path, folder), 0, f"a {path.suffix} file: the script rules here cover Python only")
              for path in sorted(folder.rglob("*")) if path.suffix in FOREIGN]
    parents = {path.parent for path in files}
    found += [(REFUSE, relative(parent, folder) or ".", 0, f"more than {FILES_PER_FOLDER} code files in one folder")
              for parent in sorted(parents) if sum(1 for path in files if path.parent == parent) > FILES_PER_FOLDER]
    if any(relative(path, folder).startswith(SCRIPTS) for path in files) and not (folder / UNIT_TEST).exists():
        found.append((REFUSE, UNIT_TEST, 0, "scripts without unit tests"))
    return found


def check_python(folder):
    files = sorted(path for path in folder.rglob("*.py") if CACHE not in path.parts)
    local_names = {path.stem for path in files if relative(path, folder).startswith(SCRIPTS)}
    found = _layout(folder, files)
    for path in files:
        where, text = relative(path, folder), read_text(path)
        if text is None:
            found.append((REFUSE, where, 0, "not readable as UTF-8"))
            continue
        found += source_findings(where, text)
        if path.parent == folder / "scripts":
            found += entry_findings(where, text, local_names)
    return found
