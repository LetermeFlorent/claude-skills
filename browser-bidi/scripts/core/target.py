import datetime
import subprocess
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote

sys.dont_write_bytecode = True

from core.common import LOCALHOST, WORK_DIR, local_url


def git(folder, *args):
    try:
        done = subprocess.run(["git", "-C", str(folder), *args], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout.strip() if done.returncode == 0 else None


def git_root(folder):
    top = git(folder, "rev-parse", "--show-toplevel")
    return Path(top).resolve() if top else None


def run_dir(root):
    base = WORK_DIR / "browser-bidi"
    if root:
        base = root / ".ia" / "browser-bidi"
        base.mkdir(parents=True, exist_ok=True)
        git_dir = git(root, "rev-parse", "--absolute-git-dir")
        if git_dir:
            exclude = Path(git_dir) / "info" / "exclude"
            exclude.parent.mkdir(parents=True, exist_ok=True)
            text = exclude.read_text(encoding="utf-8", errors="replace") if exclude.exists() else ""
            if ".ia/" not in text.split():
                exclude.write_text(text + ("" if text.endswith("\n") or not text else "\n") + ".ia/\n",
                                   encoding="utf-8")
    run = base / datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    run.mkdir(parents=True, exist_ok=True)
    return run


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class QuietServer(ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        pass


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
        self.server = QuietServer((LOCALHOST, 0), partial(QuietHandler, directory=str(folder)))
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = local_url(self.server.server_port, "/" + ("" if path.is_dir() else quote(path.name)))
        self.root = git_root(folder) or folder.resolve()

    def __enter__(self):
        return self

    def __exit__(self, *details):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
