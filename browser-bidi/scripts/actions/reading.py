import json
import sys
import time

sys.dont_write_bytecode = True

from core.common import NAV_TIMEOUT
from actions.page import nodes, plain, shared_id_of, url_of


LOG_ENTRY, FETCH_ERROR, RESPONSE_COMPLETED = "log.entryAdded", "network.fetchError", "network.responseCompleted"
CONSOLE_EVENTS = (LOG_ENTRY,)
NETWORK_EVENTS = (RESPONSE_COMPLETED, FETCH_ERROR)
DEFAULT_CHARS = 20000


def clip(text, hint):
    if len(text) <= DEFAULT_CHARS:
        return text
    return f"{text[:DEFAULT_CHARS]}\n... {len(text) - DEFAULT_CHARS} more chars, {hint}"


def wait(page):
    if page.value.isdigit():
        time.sleep(int(page.value))
        print(url_of(page))
        return
    started = time.monotonic()
    while not nodes(page, page.value):
        if time.monotonic() - started >= page.options.timeout:
            raise TimeoutError(f"still missing after {page.options.timeout} s: {page.value}")
        time.sleep(0.25)
    print(f"found after {time.monotonic() - started:.1f} s: {page.value}")


def list_nodes(kind):
    def find(page):
        found = nodes(page, page.value, kind, 12)
        print(f"found: {len(found)}")
        for item in found:
            value = item.get("value") or {}
            attributes = "".join(f' {name}="{text}"' for name, text in (value.get("attributes") or {}).items())
            print(f"<{value.get('localName')}{attributes}>")
    return find


def html(page):
    text = page.evaluate("document.documentElement.outerHTML").get("value", "")
    print(text[:int(page.value)] if page.value.isdigit() else clip(text, "pass a number"))


def text(page):
    if not page.value:
        print(clip(page.evaluate("document.body ? document.body.innerText : ''").get("value", ""),
                   "pass a selector"))
        return
    print(clip(str(page.apply("(element) => element.innerText", shared_id_of(page, page.value))),
               "pass a narrower selector"))


def evaluate(page):
    value = plain(page.evaluate(page.value))
    print(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False))


def describe(event, show_all):
    params, method = event["params"], event["method"]
    if method == LOG_ENTRY:
        return f"[{params.get('level')}] {params.get('text')}"
    if method == FETCH_ERROR:
        return f"FAILED {params.get('errorText')} {params['request'].get('url')}"
    status = params["response"].get("status", 0)
    if not show_all and status < 400:
        return None
    return f"{status} {params['request'].get('method')} {params['request'].get('url')}"


def listener(events):
    def listen(page):
        subscribed = page.call("session.subscribe", {"events": list(events), "contexts": [page.context]})
        if events is NETWORK_EVENTS:
            page.call("browsingContext.reload", {"context": page.context, "wait": "complete"}, NAV_TIMEOUT)
        words = page.value.split()
        page.session.pump(int(words[0]) if words and words[0].isdigit() else 3)
        subscription = subscribed.get("subscription")
        leave = {"subscriptions": [subscription]} if subscription else {"events": list(events)}
        page.call("session.unsubscribe", leave)
        seen, count = set(), 0
        for event in page.session.events:
            params = event.get("params", {})
            key = (event.get("method"), params.get("timestamp"), params.get("text"), str(params.get("request")))
            if event.get("method") not in events or key in seen:
                continue
            seen.add(key)
            count += 1
            line = describe(event, "all" in words)
            if line:
                print(line)
        label = "requests" if "all" in words else "requests, errors only shown"
        label = "messages" if events is CONSOLE_EVENTS else label
        print(f"{count} {label}")
    return listen


def cookies(page):
    partition = {"partition": {"type": "context", "context": page.context}}
    found = page.call("storage.getCookies", partition).get("cookies", [])
    for cookie in found:
        value = str((cookie.get("value") or {}).get("value", ""))
        print(f"{cookie.get('domain')} {cookie.get('name')}={value[:40]}{'...' if len(value) > 40 else ''}")
    print(f"{len(found)} cookies")


def clearcookies(page):
    partition = {"partition": {"type": "context", "context": page.context}}
    found = page.call("storage.getCookies", partition).get("cookies", [])
    page.call("storage.deleteCookies", partition)
    print(f"{len(found)} cookies deleted")


ACTIONS = {"wait": wait, "find": list_nodes("css"), "xpath": list_nodes("xpath"), "html": html, "text": text,
           "eval": evaluate, "console": listener(CONSOLE_EVENTS), "network": listener(NETWORK_EVENTS),
           "cookies": cookies, "clearcookies": clearcookies}
