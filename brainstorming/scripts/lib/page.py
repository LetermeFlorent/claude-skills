import html
from pathlib import Path

from common import ENCODING

ASSETS = Path(__file__).resolve().parents[2] / "assets"
FRAME = ASSETS / "frame.html"
WAITING = ASSETS / "waiting.html"
FORBIDDEN = ASSETS / "forbidden.html"
PAGE_SUFFIXES = (".html", ".htm")
FULL_DOCUMENT = ("<!doctype", "<html")
NO_SCREEN = "empty"


def screens(folder):
    return [path for path in folder.glob("*") if path.is_file() and path.suffix.lower() in PAGE_SUFFIXES]


def newest(folder):
    found = screens(folder)
    return max(found, key=lambda path: path.stat().st_mtime_ns) if found else None


def version(folder):
    screen = newest(folder)
    return f"{screen.name}:{screen.stat().st_mtime_ns}" if screen else NO_SCREEN


def is_full(text):
    return text.lstrip().lower().startswith(FULL_DOCUMENT)


def render(frame, screen_name, content, stamp):
    return (frame.replace("{{screen}}", html.escape(screen_name))
            .replace("{{version}}", html.escape(stamp))
            .replace("{{content}}", content))


def current(folder):
    frame = FRAME.read_text(encoding=ENCODING)
    screen = newest(folder)
    if screen is None:
        return render(frame, "", WAITING.read_text(encoding=ENCODING), NO_SCREEN)
    text = screen.read_text(encoding=ENCODING)
    return text if is_full(text) else render(frame, screen.name, text, version(folder))


def forbidden():
    return FORBIDDEN.read_text(encoding=ENCODING)


def asset_inside(folder, name):
    candidate = (folder / name).resolve()
    inside = candidate.parent == folder.resolve() and candidate.is_file()
    return candidate if inside else None
