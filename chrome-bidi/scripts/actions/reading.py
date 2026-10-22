import json
import time

from actions.shared import shared_id_of, nodes, plain, url_of
from actions.tabs import NAV_TIMEOUT

WAIT_STEP = 0.25
FOUND_LIMIT = 12
DEFAULT_LISTEN = 3
COOKIE_PREVIEW = 40
ERROR_STATUS = 400
LOG_ENTRY = "log.entryAdded"
FETCH_ERROR = "network.fetchError"
RESPONSE_COMPLETED = "network.responseCompleted"
SHOW_ALL = "all"
GET_COOKIES = "storage.getCookies"
CONSOLE_EVENTS = (LOG_ENTRY,)
NETWORK_EVENTS = (RESPONSE_COMPLETED, FETCH_ERROR)


def wait(page):
    if page.value.isdigit():
        time.sleep(int(page.value))
        print(url_of(page))
        return
    started = time.monotonic()
    while not nodes(page, page.value):
        if time.monotonic() - started >= page.options.timeout:
            raise TimeoutError(f"still missing after {page.options.timeout} s: {page.value}")
        time.sleep(WAIT_STEP)
    print(f"found after {time.monotonic() - started:.1f} s: {page.value}")


def list_nodes(kind):
    def find(page):
        found = nodes(page, page.value, kind, FOUND_LIMIT)
        print(f"found: {len(found)}")
        for item in found:
            value = item.get("value") or {}
            attributes = "".join(f' {name}="{text}"' for name, text in (value.get("attributes") or {}).items())
            print(f"<{value.get('localName')}{attributes}>")
    return find


def html(page):
    text = page.evaluate("document.documentElement.outerHTML").get("value", "")
    print(text[:int(page.value)] if page.value.isdigit() else text)


def text(page):
    if not page.value:
        print(page.evaluate("document.body ? document.body.innerText : ''").get("value", ""))
        return
    print(page.apply("(element) => element.innerText", shared_id_of(page, page.value)))


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
    if not show_all and status < ERROR_STATUS:
        return None
    return f"{status} {params['request'].get('method')} {params['request'].get('url')}"


def listener(events):
    def listen(page):
        subscribed = page.call("session.subscribe", {"events": list(events), "contexts": [page.context]})
        if events is NETWORK_EVENTS:
            page.call("browsingContext.reload", {"context": page.context, "wait": "complete"}, NAV_TIMEOUT)
        words = page.value.split()
        page.session.listen(int(words[0]) if words and words[0].isdigit() else DEFAULT_LISTEN)
        subscription = subscribed.get("subscription")
        unsubscribe = {"subscriptions": [subscription]} if subscription else {"events": list(events)}
        page.call("session.unsubscribe", unsubscribe)
        seen, count = set(), 0
        for event in page.session.events:
            params = event.get("params", {})
            key = (event.get("method"), params.get("timestamp"), params.get("text"), str(params.get("request")))
            if event.get("method") not in events or key in seen:
                continue
            seen.add(key)
            count += 1
            line = describe(event, SHOW_ALL in words)
            if line:
                print(line)
        requests = "requests" if SHOW_ALL in words else "requests, errors only shown"
        label = "messages" if events is CONSOLE_EVENTS else requests
        print(f"{count} {label}")
    return listen


def context_partition(page):
    return {"partition": {"type": "context", "context": page.context}}


def cookies(page):
    found = page.call(GET_COOKIES, context_partition(page)).get("cookies", [])
    for cookie in found:
        value = str((cookie.get("value") or {}).get("value", ""))
        cut = "..." if len(value) > COOKIE_PREVIEW else ""
        print(f"{cookie.get('domain')} {cookie.get('name')}={value[:COOKIE_PREVIEW]}{cut}")
    print(f"{len(found)} cookies")


def clearcookies(page):
    partition = context_partition(page)
    found = page.call(GET_COOKIES, partition).get("cookies", [])
    page.call("storage.deleteCookies", partition)
    print(f"{len(found)} cookies deleted")


ACTIONS = {"wait": wait, "find": list_nodes("css"), "xpath": list_nodes("xpath"), "html": html, "text": text,
           "eval": evaluate,
           "console": listener(CONSOLE_EVENTS), "network": listener(NETWORK_EVENTS), "cookies": cookies,
           "clearcookies": clearcookies}
