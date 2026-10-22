from pathlib import Path

from common import ENCODING, run

EXCLUDE_LINE = ".ia/"
EXCLUDE_FORMS = {".ia", ".ia/", "/.ia", "/.ia/"}
AI_FOLDER = ".ia"
REV_PARSE = "rev-parse"


def _git(arguments, cwd):
    code, out, err = run(["git", *arguments], cwd)
    if code is None:
        raise RuntimeError(err)
    return code, out.strip(), err.strip()


def toplevel(folder):
    code, out, _ = _git([REV_PARSE, "--show-toplevel"], folder)
    return Path(out) if code == 0 and out else None


def exclude_file(root):
    code, out, err = _git([REV_PARSE, "--git-path", "info/exclude"], root)
    if code != 0:
        raise RuntimeError(err or "git rev-parse --git-path info/exclude failed")
    path = Path(out)
    return path if path.is_absolute() else root / path


def has_exclude(text):
    return any(line.strip() in EXCLUDE_FORMS for line in text.splitlines())


def ensure_exclude(root):
    path = exclude_file(root)
    text = path.read_text(encoding=ENCODING) if path.exists() else ""
    if has_exclude(text):
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    glue = "" if not text or text.endswith("\n") else "\n"
    with open(path, "w", encoding=ENCODING, newline="\n") as handle:
        handle.write(text + glue + EXCLUDE_LINE + "\n")
    return True


def tracked_under(root):
    code, out, err = _git(["ls-files", "--", AI_FOLDER], root)
    if code != 0:
        raise RuntimeError(err or "git ls-files failed")
    return out.splitlines()


def ignored(root, path):
    code, _, _ = _git(["check-ignore", "-q", "--", path.as_posix()], root)
    return code == 0
