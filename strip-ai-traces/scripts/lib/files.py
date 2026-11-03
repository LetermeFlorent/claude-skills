from pathlib import Path

from common import ENCODING

SKIPPED_DIRS = {".git", "node_modules", "target", "build", "dist", "out", ".next", ".nuxt", ".venv", "venv",
                "__pycache__", ".ia", ".claude", "vendor", "coverage", ".cache", ".gradle", ".idea", ".vs"}
VALUE_DIRS = {"locales", "locale", "i18n", "l10n", "lang", "langs", "translations", "fixtures", "__snapshots__",
              "snapshots", "testdata", "test-data", "golden"}
PROSE = {".md", ".markdown", ".mdx", ".txt", ".rst", ".adoc"}
PAGE = {".html", ".htm", ".php", ".vue", ".svelte", ".astro", ".jsx", ".tsx"}
STYLE = {".css", ".scss", ".sass", ".less"}
CODE = {".py", ".js", ".mjs", ".cjs", ".ts", ".java", ".kt", ".go", ".rs", ".c", ".h", ".cpp", ".cs", ".rb", ".lua",
        ".luau", ".sh", ".ps1", ".swift", ".dart", ".scala", ".sql", ".jsx", ".tsx", ".vue", ".svelte", ".php"}
VALUES = {".po", ".pot", ".json", ".csv", ".tsv", ".snap", ".yml", ".yaml", ".toml", ".ini", ".xml", ".lock"}
DOCUMENTS = {".docx", ".xlsx", ".pptx", ".pdf", ".ipynb", ".odt", ".ods", ".odp"}
IMAGES = {".png", ".jpg", ".jpeg", ".webp", ".avif", ".heic"}
MAX_BYTES = 2 * 1024 * 1024
SNIFF = 8192


def kind_of(path):
    suffix = path.suffix.lower()
    if suffix in DOCUMENTS:
        return "document"
    if suffix in IMAGES:
        return "image"
    if VALUE_DIRS & {part.lower() for part in path.parts} or suffix in VALUES:
        return "value"
    if suffix in PROSE:
        return "prose"
    if suffix in STYLE:
        return "style"
    return "code" if suffix in CODE else "other"


def is_page(path):
    return path.suffix.lower() in PAGE


def walk(target):
    if target.is_file():
        yield target
        return
    for path in sorted(target.rglob("*")):
        relative = path.relative_to(target).parts[:-1]
        if path.is_file() and not SKIPPED_DIRS & set(relative):
            yield path


def read_text(path):
    try:
        if path.stat().st_size > MAX_BYTES:
            return None
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\0" in raw[:SNIFF]:
        return None
    try:
        return raw.decode(ENCODING)
    except UnicodeDecodeError:
        return None


def write_text(path, text):
    path.write_bytes(text.encode(ENCODING))


def relative(path, base):
    try:
        return Path(path).resolve().relative_to(base).as_posix()
    except ValueError:
        return Path(path).as_posix()
