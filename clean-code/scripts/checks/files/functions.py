import re

from lexer import PYTHON_SUFFIX, balance

RULE = 6
START = re.compile(r"(?:\bfunc\s*(?:\([^)]*\)\s*)?(?P<g>\w+)|\bfunction\b\s*\*?\s*(?P<f>\w*)|"
                   r"(?P<a>\w+)\s*[:=]\s*(?:async\s+)?(?:function\s*)?|(?P<n>\w+)\s*(?:<[^>]*>)?)\s*\(")
KEYWORDS = {"if", "for", "while", "switch", "catch", "else", "do", "try", "with", "return", "foreach", "elif",
            "synchronized", "using", "lock", "when", "match", "loop", "unless", "until", "new", "typeof", "sizeof",
            "await", "yield", "throw", "super", "this", "assert", "print", "fixed", "checked"}
PYTHON_DEF = re.compile(r"^(?P<indent>\s*)(async\s+)?def\s+(?P<name>\w+)\s*\(")
BRACE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".java", ".kt", ".kts", ".scala", ".groovy", ".rs",
                  ".go", ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".swift", ".dart", ".php"}
SIGNATURE_LINES = 8
PAIRS = {"(": ")", "[": "]", "{": "}", "<": ">"}
RECEIVERS = {"self", "cls"}


def _arguments(text):
    depth, count, current = 0, 0, ""
    for char in text:
        if char in PAIRS:
            depth += 1
        elif char in PAIRS.values() and depth:
            depth -= 1
        elif char == "," and not depth:
            count += bool(current.strip()) and current.strip() not in RECEIVERS
            current = ""
            continue
        current += char
    return count + (bool(current.strip()) and current.strip() not in RECEIVERS)


def _signature(codes, start, column):
    text, depth = "", 0
    for index in range(start, min(start + SIGNATURE_LINES, len(codes))):
        chunk = codes[index][column:] if index == start else codes[index]
        for position, char in enumerate(chunk):
            depth += (char == "(") - (char == ")")
            text += char
            if depth == 0 and char == ")":
                return text[1:-1], index, chunk[position + 1:]
        text += " "
    return None, start, ""


def _braced(codes):
    found = []
    for number, code in enumerate(codes):
        match = START.search(code)
        name = match and next(value for value in match.groupdict().values() if value is not None)
        if not match or name in KEYWORDS:
            continue
        params, close, rest = _signature(codes, number, match.end() - 1)
        tail = rest + " " + " ".join(codes[close + 1:close + 2])
        if params is None or "{" not in tail or ";" in tail.split("{")[0]:
            continue
        depth, deepest, end, opened = 0, 0, close, False
        for end in range(close, len(codes)):
            depth += codes[end].count("{") - codes[end].count("}")
            deepest, opened = max(deepest, depth), opened or "{" in codes[end]
            if depth <= 0 and opened:
                break
        found.append((name or "anonymous", number + 1, end - number + 1, _arguments(params), max(0, deepest - 1)))
    return found


def _python(codes, lines):
    found = []
    for number, code in enumerate(codes):
        match = PYTHON_DEF.match(code)
        if not match:
            continue
        indent = len(match.group("indent"))
        params, close, _ = _signature(codes, number, match.end() - 1)
        end, levels, body, carry, start = close, [0], None, 0, 0
        for end in range(close + 1, len(codes)):
            text = lines[end]
            if not text.strip():
                continue
            spaces = len(text) - len(text.lstrip())
            if spaces <= indent and not carry:
                end -= 1
                break
            body, start = body or spaces, start if carry else spaces
            carry = max(0, carry + balance(codes[end]))
            if not carry and codes[end].rstrip().endswith(":"):
                levels.append((start - body) // max(1, body - indent) + 1)
        found.append((match.group("name"), number + 1, end - number + 1, _arguments(params or ""), max(levels)))
    return found


def check(files, root, config):
    findings, measured = [], 0
    limits = {"lines": config["max_function_lines"], "params": config["max_params"], "nesting": config["max_nesting"]}

    for item in files:
        suffix = item["path"].suffix.lower()
        if not item["code"] or item["data"] or (suffix != PYTHON_SUFFIX and suffix not in BRACE_SUFFIXES):
            continue
        measured += 1
        codes = [row["code"] for row in item["rows"]]
        found = _python(codes, item["lines"]) if suffix == PYTHON_SUFFIX else _braced(codes)
        for name, line, *sizes in found:
            over = [f"{key} {size} > {limit}" for (key, limit), size in zip(limits.items(), sizes) if size > limit]
            if over:
                findings.append({"rule": RULE, "file": item["rel"], "line": line,
                                 "what": f"function {name}: " + ", ".join(over), "proof": "functions.py"})
    return findings, {"function_files": measured}
