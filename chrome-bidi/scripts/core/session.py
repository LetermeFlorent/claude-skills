import json
import sys
import time

sys.dont_write_bytecode = True

from core.common import (COMMAND_TIMEOUT, DEFAULT_PROMPT, LOCALHOST, WORK_DIR, BidiError, driver_port, http_json,
                    local_url, state_file)
from core.wsclient import WebSocket, WebSocketError


class Session:
    def __init__(self, port, url, session_id):
        self.port, self.id, self.counter, self.events = port, session_id, 0, []
        self.socket = WebSocket(url, 10)

    def pump(self, seconds, until=None):
        deadline = time.monotonic() + seconds
        while (left := deadline - time.monotonic()) > 0:
            text = self.socket.receive(left)
            if text is None:
                return None
            message = json.loads(text)
            if message.get("type") == "event":
                self.events.append(message)
            elif message.get("id") == until:
                return message
        return None

    def call(self, method, params=None, timeout=COMMAND_TIMEOUT):
        self.counter += 1
        self.socket.send(1, json.dumps({"id": self.counter, "method": method, "params": params or {}}).encode())
        message = self.pump(timeout, self.counter)
        if message is None:
            raise TimeoutError(f"no answer to {method} after {timeout} s")
        if message.get("type") == "error":
            raise BidiError(f"{message.get('error')}: {message.get('message')}")
        return message.get("result") or {}

    def classic(self, method, path, body=None):
        return http_json(method, local_url(driver_port(self.port), f"/session/{self.id}{path}"), body).get("value")

    def close(self):
        self.socket.close()


def create_session(port, prompt=DEFAULT_PROMPT):
    options = {"webSocketUrl": True, "unhandledPromptBehavior": prompt,
               "goog:chromeOptions": {"debuggerAddress": f"{LOCALHOST}:{port}"}}
    created = http_json("POST", local_url(driver_port(port), "/session"),
                        {"capabilities": {"alwaysMatch": options}})["value"]
    state = {"ws": created["capabilities"]["webSocketUrl"], "session": created["sessionId"], "prompt": prompt}
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    state_file(port).write_text(json.dumps(state))
    return Session(port, state["ws"], state["session"])


def open_session(port):
    try:
        state = json.loads(state_file(port).read_text())
    except (OSError, ValueError):
        state = {}
    if state.get("ws"):
        session = None
        try:
            session = Session(port, state["ws"], state["session"])
            session.call("browsingContext.getTree", {"maxDepth": 0}, 10)
            return session
        except (OSError, WebSocketError, BidiError):
            if session:
                session.close()
            state_file(port).unlink(missing_ok=True)
    return create_session(port, state.get("prompt", DEFAULT_PROMPT))


def first_context(session):
    return session.call("browsingContext.getTree")["contexts"][0]["context"]
