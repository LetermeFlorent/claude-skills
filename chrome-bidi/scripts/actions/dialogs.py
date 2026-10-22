from pathlib import Path

from actions.inputs import click_node
from actions.shared import PAIR, XPATH, nodes, shared_id_of
from core.common import split_value
from core.session import BidiError

REFUSALS = ("tout refuser", "refuser", "reject", "decline", "deny", "continuer sans accepter", "necessary only",
            "essential only")
ACCEPT = "accept"
LOWER_TEXT = "translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')"


def upload(page):
    selector, file = split_value(page.value, PAIR)
    path = Path(file).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"file not found: {file}")
    page.call("input.setFiles", {"context": page.context, "element": {"sharedId": shared_id_of(page, selector)},
                                 "files": [str(path)]})
    print(f"file set: {path}")


def prompt(page):
    answer, user_text = split_value(page.value, PAIR)
    params = {"context": page.context, "accept": answer == ACCEPT}
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
    found = nodes(page, f"(//button[{condition}] | //a[{condition}] | //*[@role='button'][{condition}])", XPATH)
    if not found:
        print("no reject button found")
        return
    click_node(page, found[0]["sharedId"])
    print("reject button clicked")


ACTIONS = {"upload": upload, "prompt": prompt, "rejectcookies": rejectcookies}
