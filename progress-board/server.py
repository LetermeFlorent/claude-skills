"""Local progress board: GET /<project>/<percent>[/<step>] from agents, the page at /, live updates at /events.

`server.py start` runs it in the background unless it already answers; `server.py [port]` runs it here.
The time of a point is always the server's clock on arrival; only PROGRESS_BOARD_TEST=1 lets ?t= replay one.
"""
import os
import queue
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

import store

PORT = int(os.environ.get("PROGRESS_BOARD_PORT", "8790"))
NAME_MAX = 60
PING_EVERY = 25
START_TRIES, START_WAIT = 20, 0.25
TEXT = "text/plain; charset=utf-8"
ASSET_TYPES = {".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml", ".woff2": "font/woff2"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, code: int, body: bytes, ctype: str = TEXT) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def allowed(self, write: bool) -> bool:
        host, port = self.headers.get("Host"), self.server.server_port
        origin, site = self.headers.get("Origin"), self.headers.get("Sec-Fetch-Site", "none")
        local = host in (None, f"127.0.0.1:{port}", f"localhost:{port}")
        return local and (not write or origin in (None, f"http://{host}") and site in ("none", "same-origin"))

    def do_GET(self):
        path, _, query = self.path.partition("?")
        asset = built_file(path)
        if not self.allowed(write=path not in ("/", "/events") and not asset):
            return self.send(403, b"forbidden\n")
        if path == "/":
            return self.send(200, store.PAGE.read_bytes(), "text/html; charset=utf-8")
        if path == "/events":
            return self.stream()
        if asset:
            return self.send(200, asset.read_bytes(), ASSET_TYPES.get(asset.suffix, "application/octet-stream"))
        parts = [unquote(p) for p in path.strip("/").split("/", 2)]
        if len(parts) < 2 or not parts[0] or not parts[1].isdigit():
            return self.send(400, b"usage: /<project>/<percent>[/<step>]\n")
        t = parse_qs(query).get("t", [""])[0] if os.environ.get("PROGRESS_BOARD_TEST") == "1" else ""
        now = float(t) if t.isdigit() else time.time()
        step = parts[2] if len(parts) > 2 else ""
        store.update(parts[0][:NAME_MAX], min(store.DONE, int(parts[1])), step[:NAME_MAX], now)
        self.send(200, b"ok\n")

    def do_POST(self):
        if not self.allowed(write=True):
            return self.send(403, b"forbidden\n")
        path, _, query = self.path.partition("?")
        self.send(200, b"ok\n") if store.admin(path, query) else self.send(404, b"not found\n")

    def stream(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        q: queue.Queue = queue.Queue()
        with store.lock:
            msg = store.page()
            store.listeners.append(q)
        try:
            while True:
                self.wfile.write(f"data: {msg}\n\n".encode("utf-8"))
                self.wfile.flush()
                msg = self.next_message(q)
        except OSError:
            pass
        finally:
            with store.lock:
                store.listeners.remove(q)

    def next_message(self, q: queue.Queue) -> str:
        """Pings while waiting, which is also how a closed tab is noticed."""
        while True:
            try:
                return q.get(timeout=PING_EVERY)
            except queue.Empty:
                self.wfile.write(b": ping\n\n")
                self.wfile.flush()


def built_file(path: str) -> Path | None:
    """A file of the built page; anything else, a project named "assets" included, goes to the agent API."""
    site = store.PAGE.parent.resolve()
    f = (site / unquote(path).lstrip("/")).resolve()
    return f if path.startswith("/assets/") and f.is_relative_to(site) and f.is_file() else None


def running(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def start(port: int) -> None:
    url = f"http://127.0.0.1:{port}"
    if running(port):
        return print(f"{url} already running")
    exe = Path(sys.executable)
    quiet = exe.with_name("pythonw.exe")
    exe = quiet if os.name == "nt" and quiet.exists() else exe
    flags = ({"creationflags": subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt"
             else {"start_new_session": True})
    me = Path(__file__).resolve()
    subprocess.Popen([str(exe), "-I", str(me), str(port)], cwd=store.HERE, stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **flags)
    for _ in range(START_TRIES):
        time.sleep(START_WAIT)
        if running(port):
            return print(f"{url} started")
    sys.exit(f"{url} did not start; run it in the foreground to see why: python {me} {port}")


def serve(port: int) -> ThreadingHTTPServer:
    ThreadingHTTPServer.daemon_threads, ThreadingHTTPServer.allow_reuse_address = True, os.name != "nt"
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main() -> None:
    args = sys.argv[1:]
    if args[:1] == ["start"]:
        return start(PORT)
    server = serve(int(args[0]) if args else PORT)
    threading.Thread(target=store.sweep, daemon=True).start()
    server.serve_forever()


if __name__ == "__main__":
    main()
