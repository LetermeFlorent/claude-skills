import re
import time

from actions.shared import plain, shared_id_of, stdin_text

KEYS = {"enter": chr(0xE007), "tab": chr(0xE004), "escape": chr(0xE00C), "down": chr(0xE015), "up": chr(0xE013),
        "left": chr(0xE012), "right": chr(0xE014), "backspace": chr(0xE003), "delete": chr(0xE017),
        "ctrl": chr(0xE009), "shift": chr(0xE008)}
DEFAULT_SCROLL = 600
PRESS = [{"type": "pointerDown", "button": 0}, {"type": "pointerUp", "button": 0}]
PLACE = ("(element) => { const box = element.getBoundingClientRect(); "
         "return [box.left + box.width / 2 - innerWidth / 2, box.top + box.height / 2 - innerHeight / 2, "
         "box.top >= 0 && box.left >= 0 && box.bottom <= innerHeight && box.right <= innerWidth, "
         "innerWidth, innerHeight]; }")
SETTLE_TRIES = 10
SETTLE_STEP = 0.1
KEY_DOWN = "keyDown"
KEY_UP = "keyUp"
MOUSE = "mouse"
POINTER_MOVE = "pointerMove"
WHEEL = "wheel"
HALF = 2


def perform(page, source):
    page.call("input.performActions", {"context": page.context, "actions": [source]})


def pointer(page, steps):
    perform(page, {"type": "pointer", "id": MOUSE, "parameters": {"pointerType": MOUSE}, "actions": steps})


def wheel(page, point, delta):
    x, y = point
    delta_x, delta_y = delta
    perform(page, {"type": WHEEL, "id": WHEEL,
                   "actions": [{"type": "scroll", "x": x, "y": y, "deltaX": delta_x, "deltaY": delta_y}]})


def reveal(page, shared_id):
    delta_x, delta_y, inside, width, height = page.apply(PLACE, shared_id)
    if inside:
        return
    wheel(page, (int(width // HALF), int(height // HALF)), (int(delta_x), int(delta_y)))
    for _ in range(SETTLE_TRIES):
        time.sleep(SETTLE_STEP)
        if page.apply(PLACE, shared_id)[2]:
            return


def click_node(page, shared_id):
    reveal(page, shared_id)
    origin = {"type": "element", "element": {"sharedId": shared_id}}
    pointer(page, [{"type": POINTER_MOVE, "x": 0, "y": 0, "origin": origin}, *PRESS])


def clicker(kind):
    def click(page):
        click_node(page, shared_id_of(page, page.value, kind))
        print(f"clicked {page.value}")
    return click


def coordinates(text):
    x, y = re.split(r"[,x]", text.strip())[:2]
    return int(x), int(y)


def at_point(press):
    def act(page):
        x, y = coordinates(page.value)
        pointer(page, [{"type": POINTER_MOVE, "x": x, "y": y, "origin": "viewport"}, *(PRESS if press else [])])
        print(f"{'clicked at' if press else 'mouse at'} {x},{y}")
    return act


def scroll(page):
    amount, _, place = page.value.partition("@")
    width, height = plain(page.evaluate("[innerWidth, innerHeight]"))
    x, y = coordinates(place) if place else (width // HALF, height // HALF)
    delta = int(amount) if amount.strip() else DEFAULT_SCROLL
    wheel(page, (x, y), (0, delta))
    print(f"scrolled {delta} at {x},{y}")


def keyboard(page, actions):
    perform(page, {"type": "key", "id": "keyboard", "actions": actions})


def type_text(page):
    text = page.value or stdin_text()
    keyboard(page, [{"type": kind, "value": char} for char in text for kind in (KEY_DOWN, KEY_UP)])
    print(f"typed {len(text)} characters")


def key(page):
    name, _, times = page.value.lower().partition(" x")
    combo = [KEYS.get(part, part) for part in name.strip().split("+")]
    count = int(times) if times.strip() else 1
    downs = [{"type": KEY_DOWN, "value": value} for value in combo]
    ups = [{"type": KEY_UP, "value": value} for value in reversed(combo)]
    keyboard(page, (downs + ups) * count)
    print(f"key {name.strip()} x{count}")


ACTIONS = {"click": clicker("css"), "clickxpath": clicker("xpath"), "clickxy": at_point(True), "hover": at_point(False),
           "scroll": scroll, "type": type_text, "key": key}
