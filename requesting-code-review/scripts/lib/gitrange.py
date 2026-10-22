import subprocess

TIMEOUT = 60
REV_PARSE = "rev-parse"
BASE_CANDIDATES = ("origin/main", "origin/master", "main", "master", "develop")
FIELD, RECORD = "\x1f", "\x1e"
LOG_FORMAT = f"%H{FIELD}%an{FIELD}%cn{FIELD}%s{FIELD}%B{RECORD}"


class GitError(Exception):
    pass


def git(root, *args):
    try:
        done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=TIMEOUT)
    except FileNotFoundError:
        raise GitError("git is not installed")
    except subprocess.TimeoutExpired:
        raise GitError(f"git {args[0]} timed out after {TIMEOUT} s")
    return done.returncode, done.stdout.strip(), done.stderr.strip()


def span(base, head):
    return f"{base}..{head}"


def resolve(root, rev):
    code, out, _ = git(root, REV_PARSE, "--verify", "--quiet", f"{rev}^{{commit}}")
    return out if code == 0 else None


def find_root(path):
    code, out, _ = git(path, REV_PARSE, "--show-toplevel")
    return out if code == 0 else None


def default_base(root, head):
    for name in BASE_CANDIDATES:
        if not resolve(root, name):
            continue
        code, out, _ = git(root, "merge-base", name, head)
        if code == 0 and out != head:
            return out, f"merge-base with {name}"
    parent = resolve(root, f"{head}~1")
    return (parent, "parent of head") if parent else (None, "")


def changed_files(root, base, head):
    code, out, err = git(root, "diff", "--name-status", "--no-renames", f"{base}...{head}")
    if code != 0:
        raise GitError(err or "git diff failed")
    return [line.split("\t", 1) for line in out.splitlines() if "\t" in line]


def commits(root, base, head):
    code, out, err = git(root, "log", f"--format={LOG_FORMAT}", span(base, head))
    if code != 0:
        raise GitError(err or "git log failed")
    rows = []
    for record in filter(None, (part.strip() for part in out.split(RECORD))):
        sha, author, committer, subject, body = record.split(FIELD, 4)
        rows.append({"sha": sha, "author": author, "committer": committer, "subject": subject, "body": body})
    return rows


def branch_name(root):
    return git(root, "branch", "--show-current")[1]
