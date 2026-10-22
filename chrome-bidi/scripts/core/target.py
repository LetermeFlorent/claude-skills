import datetime
import subprocess
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote

from core.common import ENCODING, LOCALHOST, TOOL, WORK_DIR, local_url

GIT_TIMEOUT = 30
STAMP = "%Y-%m-%d-%H%M%S"
IA_DIR = ".ia"
IGNORED = IA_DIR + "/"
REV_PARSE = "rev-parse"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def git(folder, *args):
    try:
        done = subprocess.run(["git", "-C", str(folder), *args], capture_output=True, text=True, timeout=GIT_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout.strip() if done.returncode == 0 else None


def git_root(folder):
    top = git(folder, REV_PARSE, "--show-toplevel")
    return Path(top).resolve() if top else None


def project_root(folder):
    return git_root(folder) or folder.resolve()


def tool_dir(root):
    folder = root / IA_DIR / TOOL
    folder.mkdir(parents=True, exist_ok=True)
    git_dir = git(root, REV_PARSE, "--absolute-git-dir")
    if git_dir:
        exclude = Path(git_dir) / "info" / "exclude"
        exclude.parent.mkdir(parents=True, exist_ok=True)
        text = exclude.read_text(encoding=ENCODING, errors="replace") if exclude.exists() else ""
        if IGNORED not in text.split():
            joint = "" if text.endswith("\n") or not text else "\n"
            exclude.write_text(text + joint + IGNORED + "\n", encoding=ENCODING)
    return folder


def run_dir(root):
    base = tool_dir(root) if root else WORK_DIR / TOOL
    run = base / datetime.datetime.now().strftime(STAMP)
    run.mkdir(parents=True, exist_ok=True)
    return run


class Target:
    def __init__(self, text):
        self.url, self.root, self.server = text, None, None
        path = Path(text)
        if "://" in text:
            self.root = git_root(Path.cwd())
            return
        if not path.exists():
            raise FileNotFoundError(f"neither a url with a scheme nor an existing file or folder: {text}")
        folder = path if path.is_dir() else path.parent
        self.server = ThreadingHTTPServer((LOCALHOST, 0), partial(QuietHandler, directory=str(folder)))
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        page = "" if path.is_dir() else quote(path.name)
        self.url = local_url(self.server.server_port, f"/{page}")
        self.root = project_root(folder)

    def __enter__(self):
        return self

    def __exit__(self, *details):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
