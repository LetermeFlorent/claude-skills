import re

from common import DECODE_ERRORS, ENCODING

MEGABYTE = 1_000_000
LARGE_BYTES = 5 * MEGABYTE
SHOWN = 4
TOOLING = re.compile(r"(^|/)(\.ia|\.claude|\.cursor|\.aider[^/]*)(/|$)|(^|/)CLAUDE(\.local)?\.md$")
SECRET_NAME = re.compile(r"(^|/)(\.env(\.(?!(example|sample|template|dist)$)[^/]+)?|id_(rsa|ed25519|ecdsa)[^/]*"
                         r"|[^/]+\.(pem|key|p12|pfx|keystore|jks)|[^/]*credentials[^/]*\.json"
                         r"|[^/]*service-account[^/]*\.json|\.npmrc|\.pypirc|\.netrc)$")
SECRET_TEXT = re.compile(r"\b(sk_live_[0-9A-Za-z]{10,}|sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]{20,}"
                         r"|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}"
                         r"|xox[abprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35})|-----BEGIN [A-Z ]*PRIVATE KEY-----")
ARTIFACT = re.compile(r"(^|/)(node_modules|dist|build|out|target|coverage|__pycache__|\.next|\.nuxt|\.turbo"
                      r"|\.cache|\.gradle|\.venv|venv|\.pytest_cache|\.mypy_cache)(/|$)"
                      r"|\.(pyc|pyo|log|tmp|swp)$|(^|/)(\.DS_Store|Thumbs\.db|desktop\.ini)$")
KINDS = ("tooling", "secret", "artifact", "large", "ok")
TOOLING_KIND, SECRET_KIND, ARTIFACT_KIND, LARGE_KIND, OK_KIND = KINDS


def _mask(value):
    return f"{value[:SHOWN]}... ({len(value)} chars)"


def _secret_in(file):
    try:
        text = file.read_text(encoding=ENCODING, errors=DECODE_ERRORS)
    except OSError:
        return None
    for number, line in enumerate(text.splitlines(), 1):
        found = SECRET_TEXT.search(line)
        if found:
            return f"line {number}: {_mask(found.group(0))}"
    return None


def classify(root, entry):
    path, file = entry["path"], root / entry["path"]
    if TOOLING.search(path):
        return TOOLING_KIND, "AI tooling path, never committed"
    if SECRET_NAME.search(path) and not entry["deleted"]:
        return SECRET_KIND, "file name of a secret store"
    size = file.stat().st_size if file.is_file() else 0
    leaked = _secret_in(file) if file.is_file() and size < LARGE_BYTES else None
    if leaked:
        return SECRET_KIND, leaked
    if entry["new"] and ARTIFACT.search(path):
        return ARTIFACT_KIND, "generated file, belongs in .gitignore"
    if entry["new"] and size >= LARGE_BYTES:
        return LARGE_KIND, f"{size // MEGABYTE} MB new file"
    return OK_KIND, ""
