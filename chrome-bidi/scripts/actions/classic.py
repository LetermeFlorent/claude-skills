from actions.shared import CSS, PAIR, XPATH, locator_kind, stdin_text
from core.common import split_value

ELEMENT_KEY = "element-6066-11e4-a52e-4f735466cecf"
STRATEGIES = {XPATH: XPATH, CSS: "css selector"}
POST = "POST"


def strategy(selector):
    return STRATEGIES[locator_kind(selector)]


def focus_window(page):
    if page.options.frame:
        raise RuntimeError("fill and select act on the top page of a tab, not inside --frame")
    page.session.classic(POST, "/window", {"handle": page.context})


def find(page, using, selector, base=""):
    return page.session.classic(POST, f"{base}/element", {"using": using, "value": selector})[ELEMENT_KEY]


def literal(text):
    if "'" not in text:
        return f"'{text}'"
    if '"' not in text:
        return f'"{text}"'
    return "concat(" + ", \"'\", ".join(f"'{part}'" for part in text.split("'")) + ")"


def fill(page):
    selector, text = split_value(page.value, PAIR)
    text = text or stdin_text()
    focus_window(page)
    element = find(page, strategy(selector), selector)
    page.session.classic(POST, f"/element/{element}/value", {"text": text})
    print(f"filled {selector} with {len(text)} characters")


def select(page):
    selector, label = split_value(page.value, PAIR)
    focus_window(page)
    menu = find(page, strategy(selector), selector)
    option = find(page, XPATH, f".//option[normalize-space()={literal(label)}]", f"/element/{menu}")
    page.session.classic(POST, f"/element/{option}/click", {})
    print(f"selected {label} in {selector}")


ACTIONS = {"fill": fill, "select": select}
