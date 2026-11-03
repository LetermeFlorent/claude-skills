import re
import sys
import time

sys.dont_write_bytecode = True

from actions.page import plain, shared_id_of, stdin_text


KEYS = {"enter": 0xE007, "tab": 0xE004, "escape": 0xE00C, "down": 0xE015, "up": 0xE013, "left": 0xE012,
        "right": 0xE014, "backspace": 0xE003, "delete": 0xE017, "ctrl": 0xE009, "shift": 0xE008}
PRESS = [{"type": "pointerDown", "button": 0}, {"type": "pointerUp", "button": 0}]
PLACE = ("(element) => { const box = element.getBoundingClientRect(); "
         "return [box.left + box.width / 2 - innerWidth / 2, box.top + box.height / 2 - innerHeight / 2, "
         "box.top >= 0 && box.left >= 0 && box.bottom <= innerHeight && box.right <= innerWidth, "
         "innerWidth, innerHeight]; }")


def perform(page, source):
    page.call("input.performActions", {"context": page.context, "actions": [source]})


def pointer(page, steps):
    perform(page, {"type": "pointer", "id": "mouse", "parameters": {"pointerType": "mouse"}, "actions": steps})


def wheel(page, point, delta):
    perform(page, {"type": "wheel", "id": "wheel", "actions": [
        {"type": "scroll", "x": point[0], "y": point[1], "deltaX": delta[0], "deltaY": delta[1]}]})


def reveal(page, shared_id):
    delta_x, delta_y, inside, width, height = page.apply(PLACE, shared_id)
    if inside:
        return
    wheel(page, (int(width // 2), int(height // 2)), (int(delta_x), int(delta_y)))
    for _ in range(10):
        time.sleep(0.1)
        if page.apply(PLACE, shared_id)[2]:
            return


def click_node(page, shared_id):
    reveal(page, shared_id)
    origin = {"type": "element", "element": {"sharedId": shared_id}}
    pointer(page, [{"type": "pointerMove", "x": 0, "y": 0, "origin": origin}, *PRESS])


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
        pointer(page, [{"type": "pointerMove", "x": x, "y": y, "origin": "viewport"}, *(PRESS if press else [])])
        print(f"{'clicked at' if press else 'mouse at'} {x},{y}")
    return act


def scroll(page):
    amount, _, place = page.value.partition("@")
    width, height = plain(page.evaluate("[innerWidth, innerHeight]"))
    x, y = coordinates(place) if place else (width // 2, height // 2)
    delta = int(amount) if amount.strip() else 600
    wheel(page, (x, y), (0, delta))
    print(f"scrolled {delta} at {x},{y}")


def keyboard(page, actions):
    perform(page, {"type": "key", "id": "keyboard", "actions": actions})


def type_text(page):
    typed = page.value or stdin_text()
    keyboard(page, [{"type": kind, "value": char} for char in typed for kind in ("keyDown", "keyUp")])
    print(f"typed {len(typed)} characters")


def key(page):
    name, _, times = page.value.lower().partition(" x")
    combo = [chr(KEYS[part]) if part in KEYS else part for part in name.strip().split("+")]
    count = int(times) if times.strip() else 1
    downs = [{"type": "keyDown", "value": value} for value in combo]
    ups = [{"type": "keyUp", "value": value} for value in reversed(combo)]
    keyboard(page, (downs + ups) * count)
    print(f"key {name.strip()} x{count}")


ACTIONS = {"click": clicker("css"), "clickxpath": clicker("xpath"), "clickxy": at_point(True),
           "hover": at_point(False), "scroll": scroll, "type": type_text, "key": key}
