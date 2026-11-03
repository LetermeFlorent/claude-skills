import sys
from pathlib import Path

sys.dont_write_bytecode = True

from core.common import BidiError, split_value
from actions.inputs import click_node
from actions.page import locator_kind, nodes, shared_id_of, stdin_text


REFUSALS = ("tout refuser", "refuser", "reject", "decline", "deny", "continuer sans accepter", "necessary only",
            "essential only")
LOWER_TEXT = "translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')"
ELEMENT_KEY = "element-6066-11e4-a52e-4f735466cecf"


def upload(page):
    selector, file = split_value(page.value, 2)
    path = Path(file).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"file not found: {file}")
    page.call("input.setFiles", {"context": page.context, "element": {"sharedId": shared_id_of(page, selector)},
                                 "files": [str(path)]})
    print(f"file set: {path}")


def prompt(page):
    answer, user_text = split_value(page.value, 2)
    params = {"context": page.context, "accept": answer == "accept"}
    if user_text:
        params["userText"] = user_text
    try:
        page.call("browsingContext.handleUserPrompt", params)
    except BidiError as error:
        if "no such alert" not in str(error):
            raise
        print("no open prompt")
        return
    print("prompt accepted" if params["accept"] else "prompt dismissed")


def rejectcookies(page):
    condition = " or ".join(f"contains({LOWER_TEXT},'{word}')" for word in REFUSALS)
    found = nodes(page, f"(//button[{condition}] | //a[{condition}] | //*[@role='button'][{condition}])", "xpath")
    if not found:
        print("no reject button found")
        return
    click_node(page, found[0]["sharedId"])
    print("reject button clicked")


def literal(value):
    if "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    return "concat(" + ", \"'\", ".join(f"'{part}'" for part in value.split("'")) + ")"


def classic_find(page, using, selector, base=""):
    return page.session.classic("POST", f"{base}/element", {"using": using, "value": selector})[ELEMENT_KEY]


def focus_window(page):
    if page.options.frame:
        raise RuntimeError("fill and select act on the top page of a tab, not inside --frame")
    page.session.classic("POST", "/window", {"handle": page.context})


def fill(page):
    selector, typed = split_value(page.value, 2)
    typed = typed or stdin_text()
    focus_window(page)
    element = classic_find(page, "xpath" if locator_kind(selector) == "xpath" else "css selector", selector)
    page.session.classic("POST", f"/element/{element}/value", {"text": typed})
    print(f"filled {selector} with {len(typed)} characters")


def select(page):
    selector, label = split_value(page.value, 2)
    focus_window(page)
    menu = classic_find(page, "xpath" if locator_kind(selector) == "xpath" else "css selector", selector)
    option = classic_find(page, "xpath", f".//option[normalize-space()={literal(label)}]", f"/element/{menu}")
    page.session.classic("POST", f"/element/{option}/click", {})
    print(f"selected {label} in {selector}")


ACTIONS = {"upload": upload, "prompt": prompt, "rejectcookies": rejectcookies, "fill": fill, "select": select}
