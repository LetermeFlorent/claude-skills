import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from actions import capture, classic, dialogs, emulation, inputs, reading, tabs
from actions.shared import Page, flatten
from core.common import guard, port_free
from core.session import open_session

DEFAULT_WAIT = 10
ACTIONS = {name: action for module in (tabs, reading, inputs, dialogs, capture, emulation, classic)
           for name, action in module.ACTIONS.items()}


def frame_context(top, part):
    found = next((entry for entry in flatten([top]) if part in entry.get("url", "")), None)
    if not found:
        raise LookupError(f"no frame whose url contains {part}")
    return found["context"]


def main():
    parser = argparse.ArgumentParser(description="Run one action on the Chrome started by launch.py.")
    parser.add_argument("action", choices=sorted(ACTIONS))
    parser.add_argument("value", nargs="*", help="parts separated by | when the action takes two")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--tab", type=int, help="tab index from the tabs action, 0 when missing")
    parser.add_argument("--frame", help="part of the url of the iframe to act in")
    parser.add_argument("--timeout", type=float, default=DEFAULT_WAIT, help="seconds for wait <selector>")
    options = parser.parse_args()
    options.value = " ".join(options.value)
    if port_free(options.port):
        raise LookupError(f"no Chrome listens on port {options.port}, start one with launch.py --port {options.port}")
    session = open_session(options.port)
    try:
        contexts = session.call("browsingContext.getTree")["contexts"]
        index = options.tab or 0
        if index >= len(contexts):
            raise LookupError(f"tab {index} not found, {len(contexts)} open")
        context = frame_context(contexts[index], options.frame) if options.frame else contexts[index]["context"]
        ACTIONS[options.action](Page(session, context, contexts, options))
    finally:
        session.close()


if __name__ == "__main__":
    guard(main, "check the port with the tabs action; if the session is gone, run launch.py again on the same port, "
                "or use the WebDriver HTTP API on port+1000 as SKILL.md describes")
