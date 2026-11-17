import os
import re

OTHER = "other"
EXT_LANG = {
    ".py": "python", ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "typescript", ".tsx": "typescript", ".go": "go", ".rs": "rust", ".java": "java", ".kt": "kotlin",
    ".kts": "kotlin", ".cs": "csharp", ".c": "c", ".h": "c", ".cc": "c", ".cpp": "c", ".cxx": "c", ".hpp": "c",
    ".hh": "c", ".php": "php", ".rb": "ruby", ".swift": "swift", ".lua": "lua", ".luau": "lua",
    ".sh": "shell", ".bash": "shell", ".zsh": "shell",
}
COMMON = frozenset({"main", "init", "get", "set", "run", "name", "self", "cls", "this", "args", "kwargs", "value",
                    "values", "data", "result", "results", "items", "item", "path", "text", "line", "lines",
                    "file", "files", "key", "keys", "type", "types", "error", "test", "none", "true", "false",
                    "null", "str", "int", "len", "map", "list", "dict", "count", "index", "size", "String", "replace",
                    "split", "join", "read_text", "write_text", "append", "format", "update", "start", "stop", "close",
                    "open", "read", "write", "add", "remove", "strip", "copy", "sort", "exists", "resolve"})
KEYWORDS = frozenset({"if", "for", "while", "switch", "catch", "return", "else", "function", "sizeof", "defined",
                      "elif", "do", "new", "delete", "throw", "using", "foreach", "synchronized", "when", "match"})
MODS = (r"(?:(?:public|private|protected|static|final|abstract|synchronized|override|async|virtual|internal"
        r"|sealed|partial|readonly|unsafe|extern|new)\s+)")
SWIFT_MODS = r"(?:(?:public|private|internal|fileprivate|open|static|final|override|mutating)\s+)*"
KOTLIN_MODS = r"(?:(?:public|private|protected|internal|override|open|suspend|inline|abstract)\s+)*"
RUST_VIS = r"(?:pub(?:\([^)]*\))?\s+)?"
QUOTED = r"['\"]([^'\"]+)['\"]"
JS = {
    "defs": [
        ("function", r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*([\w$]+)"),
        ("class", r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([\w$]+)"),
        ("type", r"^\s*(?:export\s+)?(?:declare\s+)?(?:interface|type|enum)\s+([\w$]+)"),
        ("const", r"^(?:export\s+)?(?:const|let|var)\s+([\w$]+)\s*[=:]"),
        ("method", r"^\s+(?:(?:public|private|protected|static|async|readonly|get|set)\s+)*([\w$]+)\s*"
                   r"\([^)]*\)\s*(?::\s*[^{=]+)?\{\s*$"),
    ],
    "imports": [r"(?:import|export)\s[^'\"]*?\sfrom\s*" + QUOTED, r"\bimport\s*" + QUOTED,
                r"\brequire\(\s*" + QUOTED + r"\s*\)", r"\bimport\(\s*" + QUOTED + r"\s*\)"],
}
JAVA = {
    "defs": [
        ("class", rf"^\s*{MODS}*(?:class|interface|enum|record|struct|@interface)\s+(\w+)"),
        ("const", rf"^\s*{MODS}*(?:static\s+final|const)\s+[\w<>\[\],.?]+\s+([A-Z][A-Z0-9_]*)\s*="),
        ("method", rf"^\s*{MODS}+[\w<>\[\],.?]+\s+(\w+)\s*\("),
    ],
    "imports": [r"^\s*import\s+(?:static\s+)?([\w.]+)"],
}
RULES = {
    "python": {"defs": [], "imports": []},
    "javascript": JS,
    "typescript": JS,
    "java": JAVA,
    "csharp": {**JAVA, "imports": [r"^\s*using\s+(?:static\s+)?([\w.]+)\s*;"]},
    "go": {
        "defs": [("function", r"^func\s+(?:\([^)]*\)\s*)?(\w+)"), ("type", r"^type\s+(\w+)"),
                 ("const", r"^(?:const|var)\s+(\w+)")],
        "imports": [r"^\s*import\s+(?:[\w.]+\s+)?\"([^\"]+)\"", r"^\s+(?:[\w.]+\s+)?\"([\w./-]+)\"\s*$"],
    },
    "rust": {
        "defs": [("function", rf"^\s*{RUST_VIS}(?:async\s+|unsafe\s+|const\s+)*fn\s+(\w+)"),
                 ("type", rf"^\s*{RUST_VIS}(?:struct|enum|trait|type|union)\s+(\w+)"),
                 ("const", rf"^\s*{RUST_VIS}(?:const|static)\s+(\w+)")],
        "imports": [r"^\s*(?:pub\s+)?use\s+([\w:]+)", r"^\s*(?:pub\s+)?mod\s+(\w+)\s*;"],
    },
    "kotlin": {
        "defs": [("function", rf"^\s*{KOTLIN_MODS}fun\s+(?:<[^>]+>\s*)?(?:[\w.]+\.)?(\w+)"),
                 ("class", r"^\s*(?:(?:data|sealed|enum|abstract|open|private|internal)\s+)*"
                           r"(?:class|interface|object)\s+(\w+)"),
                 ("const", r"^(?:private\s+|internal\s+)?(?:const\s+)?val\s+([A-Z][A-Z0-9_]*)")],
        "imports": [r"^\s*import\s+([\w.]+)"],
    },
    "c": {
        "defs": [("type", r"^\s*(?:typedef\s+)?(?:class|struct|enum|union|namespace)\s+(\w+)"),
                 ("const", r"^\s*#\s*define\s+(\w+)"),
                 ("function", r"^(?!\s)(?:[\w:<>,*&]+\s+)+[*&]*(\w+)\s*\([^;]*$")],
        "imports": [r"^\s*#\s*include\s*[<\"]([^>\"]+)[>\"]"],
    },
    "php": {
        "defs": [("function", r"^\s*(?:(?:public|private|protected|static|abstract|final)\s+)*function\s+&?(\w+)"),
                 ("class", r"^\s*(?:abstract\s+|final\s+)?(?:class|interface|trait|enum)\s+(\w+)"),
                 ("const", r"^\s*(?:(?:public|private|protected)\s+)?const\s+(\w+)")],
        "imports": [r"^\s*use\s+([\w\\]+)", r"(?:require|include)(?:_once)?\s*\(?\s*" + QUOTED],
    },
    "ruby": {
        "defs": [("function", r"^\s*def\s+(?:self\.)?(\w+[?!=]?)"), ("class", r"^\s*(?:class|module)\s+(\w+)"),
                 ("const", r"^\s*([A-Z][A-Z0-9_]+)\s*=")],
        "imports": [r"^\s*require(?:_relative)?\s+" + QUOTED],
    },
    "swift": {
        "defs": [("function", rf"^\s*{SWIFT_MODS}func\s+(\w+)"),
                 ("class", rf"^\s*{SWIFT_MODS}(?:class|struct|enum|protocol|extension|actor)\s+(\w+)")],
        "imports": [r"^\s*import\s+(\w+)"],
    },
    "lua": {
        "defs": [("function", r"^\s*(?:local\s+)?function\s+(?:[\w.]+[.:])?(\w+)"),
                 ("function", r"^\s*(?:local\s+)?(\w+)\s*=\s*function"),
                 ("type", r"^\s*(?:export\s+)?type\s+(\w+)\s*="), ("const", r"^local\s+([A-Z][A-Z0-9_]+)\s*=")],
        "imports": [r"\brequire\(\s*" + QUOTED + r"\s*\)", r"\brequire\(\s*[\w.]*?(\w+)\s*\)"],
    },
    "shell": {
        "defs": [("function", r"^\s*function\s+([\w-]+)"), ("function", r"^\s*([\w-]+)\s*\(\)")],
        "imports": [r"^\s*(?:source|\.)\s+[\"']?([^\s\"';]+)"],
    },
}
COMPILED = {}


def lang_of(path):
    return EXT_LANG.get(os.path.splitext(path)[1].lower())


def rules_for(lang):
    if lang not in COMPILED:
        raw = RULES[lang]
        COMPILED[lang] = {"defs": [(kind, re.compile(p, re.M)) for kind, p in raw["defs"]],
                          "imports": [re.compile(p, re.M) for p in raw["imports"]]}
    return COMPILED[lang]
