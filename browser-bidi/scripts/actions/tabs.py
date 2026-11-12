import sys
import time
from urllib.parse import urlsplit

sys.dont_write_bytecode = True

from core.browser import stop
from core.common import BLANK, NAV_TIMEOUT
from actions.page import index_of, tree, url_of


def reusable_tab(page):
    host = urlsplit(page.value).hostname
    same_site = [entry for entry in page.contexts
                 if entry["url"].startswith("http") and urlsplit(entry["url"]).hostname == host]
    blank = [entry for entry in page.contexts if entry["url"] == BLANK]
    found = (same_site or blank or [None])[0]
    return found["context"] if found else page.call("browsingContext.create", {"type": "tab"})["context"]


def nav(page):
    context = page.context
    if page.options.tab is None and page.options.frame is None:
        context = reusable_tab(page)
        page.call("browsingContext.activate", {"context": context})
    page.call("browsingContext.navigate", {"context": context, "url": page.value, "wait": "complete"}, NAV_TIMEOUT)
    print(f"tab {index_of(tree(page), context)}")
    print(url_of(page, context))


def newtab(page):
    created = page.call("browsingContext.create", {"type": "tab"})["context"]
    if page.value:
        page.call("browsingContext.navigate", {"context": created, "url": page.value, "wait": "none"})
    print(f"tab {index_of(tree(page), created)} opened")


def tabs(page):
    for index, entry in enumerate(tree(page)):
        print(f"{index} {entry['url']}")


def closetab(page):
    if len(page.contexts) <= 1:
        raise RuntimeError("last open tab, use the close action to shut the browser")
    page.call("browsingContext.close", {"context": page.context})
    print(f"tab {page.options.tab or 0} closed, {len(page.contexts) - 1} left")


def activate(page):
    page.call("browsingContext.activate", {"context": page.context})
    print(f"tab {page.options.tab or 0} in front")


def url(page):
    print(url_of(page))
    print(page.evaluate("document.title").get("value", ""))


def history(step):
    def move(page):
        page.call("browsingContext.traverseHistory", {"context": page.context, "delta": step})
        time.sleep(0.8)
        print(url_of(page))
    return move


def reload(page):
    page.call("browsingContext.reload", {"context": page.context, "wait": "complete"}, NAV_TIMEOUT)
    print(url_of(page))


def close(page):
    print(stop(page.options.port, page.session))


ACTIONS = {"nav": nav, "newtab": newtab, "tabs": tabs, "closetab": closetab, "activate": activate, "url": url,
           "back": history(-1), "forward": history(1), "reload": reload, "close": close}
