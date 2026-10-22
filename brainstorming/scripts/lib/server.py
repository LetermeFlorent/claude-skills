import json
import mimetypes
import os
import secrets
import time
from datetime import datetime
from http import HTTPStatus
from http.cookies import CookieError, SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, unquote, urlsplit

from choices import record
from common import ENCODING, HOST, address, write_json
from page import asset_inside, current, forbidden, version
from session import CHOICE_ROUTE, CHOICES, FILES_ROUTE, INFO, KEY_HEADER, LOG, SCREENS, STOP_ROUTE, VERSION_ROUTE

COOKIE = "concevoir"
BODY_LIMIT = 65536
TICK = 1.0
SECONDS_PER_MINUTE = 60
HTML = "text/html; charset=utf-8"
TEXT = "text/plain; charset=utf-8"
NOT_FOUND = "not found"
KEY_BYTES = 16
BINARY = "application/octet-stream"


def log(folder, text):
    with open(folder / LOG, "a", encoding=ENCODING) as handle:
        handle.write(f"{datetime.now():%H:%M:%S} {text}\n")


class Companion(HTTPServer):
    def __init__(self, folder, key):
        super().__init__((HOST, 0), Handler)
        self.folder, self.key, self.timeout = folder, key, TICK
        self.last, self.stopping = time.monotonic(), False


class Handler(BaseHTTPRequestHandler):
    def log_message(self, form, *values):
        return None

    def _cookie(self):
        try:
            jar = SimpleCookie(self.headers.get("Cookie", ""))
        except CookieError:
            return ""
        return jar[COOKIE].value if COOKIE in jar else ""

    def _given_key(self):
        query = parse_qs(urlsplit(self.path).query)
        return query.get("key", [""])[0] or self.headers.get(KEY_HEADER, "") or self._cookie()

    def _send(self, status, body, kind=HTML):
        data = body if isinstance(body, bytes) else body.encode(ENCODING)
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if getattr(self, "granted", False):
            self.send_header("Set-Cookie", f"{COOKIE}={self.server.key}; Path=/; HttpOnly; SameSite=Strict")
        self.end_headers()
        self.wfile.write(data)

    def _route(self):
        return urlsplit(self.path).path

    def _allowed(self):
        self.granted = secrets.compare_digest(self._given_key().encode(ENCODING), self.server.key.encode(ENCODING))
        if self.granted:
            return True
        self._send(HTTPStatus.FORBIDDEN, forbidden())
        return False

    def do_GET(self):
        if not self._allowed():
            return
        route, screens = self._route(), self.server.folder / SCREENS
        if route == VERSION_ROUTE:
            return self._send(HTTPStatus.OK, version(screens), TEXT)
        self.server.last = time.monotonic()
        if route.startswith(FILES_ROUTE):
            return self._file(screens, unquote(route[len(FILES_ROUTE):]))
        self._send(HTTPStatus.OK, current(screens))

    def _file(self, screens, name):
        found = asset_inside(screens, name)
        if found is None:
            return self._send(HTTPStatus.NOT_FOUND, NOT_FOUND, TEXT)
        self._send(HTTPStatus.OK, found.read_bytes(), mimetypes.guess_type(found.name)[0] or BINARY)

    def do_POST(self):
        if not self._allowed():
            return
        self.server.last = time.monotonic()
        if self._route() == STOP_ROUTE:
            self.server.stopping = True
            return self._send(HTTPStatus.OK, "stopping", TEXT)
        if self._route() != CHOICE_ROUTE:
            return self._send(HTTPStatus.NOT_FOUND, NOT_FOUND, TEXT)
        self._choice()

    def _choice(self):
        size = min(int(self.headers.get("Content-Length") or 0), BODY_LIMIT)
        try:
            screen, entry = record(self.server.folder / CHOICES, json.loads(self.rfile.read(size) or b"{}"))
        except ValueError as error:
            return self._send(HTTPStatus.BAD_REQUEST, str(error), TEXT)
        log(self.server.folder, f"{'sent' if entry['sent'] else 'ticked'} {screen}")
        self._send(HTTPStatus.OK, "ok", TEXT)


def serve(folder, idle_minutes):
    server = Companion(folder, secrets.token_urlsafe(KEY_BYTES))
    port = server.server_address[1]
    url = address(port, f"/?key={server.key}")
    write_json(folder / INFO, {"port": port, "key": server.key, "pid": os.getpid(), "url": url})
    log(folder, f"listening on {url}")
    limit = idle_minutes * SECONDS_PER_MINUTE
    while not server.stopping and time.monotonic() - server.last < limit:
        server.handle_request()
    server.server_close()
    log(folder, "stopped" if server.stopping else f"stopped, idle for {idle_minutes} min")
    (folder / INFO).unlink(missing_ok=True)
