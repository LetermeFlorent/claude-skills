import json
import time
import urllib.error
import urllib.request

from core.common import ENCODING, LOCALHOST, WORK_DIR, driver_port, local_url
from core.wsclient import WebSocket, WebSocketError

CONNECT_TIMEOUT = 10
COMMAND_TIMEOUT = 30
DEFAULT_PROMPT = "dismiss"
EVENT = "event"
ERROR = "error"
LOCAL = urllib.request.build_opener(urllib.request.ProxyHandler({}))


class BidiError(Exception):
    pass


def state_file(port):
    return WORK_DIR / f"chrome-{port}.session"


def http_json(method, url, body=None, timeout=COMMAND_TIMEOUT):
    data = None if body is None else json.dumps(body).encode(ENCODING)
    request = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with LOCAL.open(request, timeout=timeout) as response:
            return json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as error:
        try:
            detail = json.loads(error.read() or b"{}").get("value") or {}
        except ValueError:
            detail = {}
        raise BidiError(f"{detail.get('error', error.code)}: {detail.get('message', error.reason)}") from None


class Session:
    def __init__(self, port, socket, session_id):
        self.port = port
        self.socket = socket
        self.id = session_id
        self.counter = 0
        self.events = []

    def call(self, method, params=None, timeout=COMMAND_TIMEOUT):
        self.counter += 1
        self.socket.send_text(json.dumps({"id": self.counter, "method": method, "params": params or {}}))
        deadline = time.monotonic() + timeout
        while (left := deadline - time.monotonic()) > 0:
            text = self.socket.receive(left)
            if text is None:
                break
            message = json.loads(text)
            if message.get("type") == EVENT:
                self.events.append(message)
            elif message.get("id") == self.counter:
                if message.get("type") == ERROR:
                    raise BidiError(f"{message.get('error')}: {message.get('message')}")
                return message.get("result") or {}
        raise TimeoutError(f"no answer to {method} after {timeout} s")

    def listen(self, seconds):
        deadline = time.monotonic() + seconds
        while (left := deadline - time.monotonic()) > 0:
            text = self.socket.receive(left)
            if text is not None and (message := json.loads(text)).get("type") == EVENT:
                self.events.append(message)

    def classic(self, method, path, body=None):
        url = local_url(driver_port(self.port), f"/session/{self.id}{path}")
        return http_json(method, url, body).get("value")

    def close(self):
        self.socket.close()


def create_session(port, prompt=DEFAULT_PROMPT):
    options = {"debuggerAddress": f"{LOCALHOST}:{port}"}
    capabilities = {"webSocketUrl": True, "unhandledPromptBehavior": prompt, "goog:chromeOptions": options}
    created = http_json("POST", local_url(driver_port(port), "/session"),
                        {"capabilities": {"alwaysMatch": capabilities}})["value"]
    state = {"ws": created["capabilities"]["webSocketUrl"], "session": created["sessionId"], "prompt": prompt}
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    state_file(port).write_text(json.dumps(state), encoding=ENCODING)
    return Session(port, WebSocket.connect(state["ws"], CONNECT_TIMEOUT), state["session"])


def open_session(port):
    path = state_file(port)
    try:
        state = json.loads(path.read_text(encoding=ENCODING))
    except (OSError, ValueError):
        state = {}
    if state.get("ws"):
        session = None
        try:
            session = Session(port, WebSocket.connect(state["ws"], CONNECT_TIMEOUT), state["session"])
            session.call("browsingContext.getTree", {"maxDepth": 0}, CONNECT_TIMEOUT)
            return session
        except (OSError, WebSocketError, BidiError):
            if session:
                session.close()
            path.unlink(missing_ok=True)
    return create_session(port, state.get("prompt", DEFAULT_PROMPT))
