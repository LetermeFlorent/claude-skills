import sys

from core.session import COMMAND_TIMEOUT

XPATH_START = ("/", "(")
XPATH = "xpath"
CSS = "css"
PAIR = 2
EXCEPTION = "exception"
SCRIPT_FAILED = "page script failed: {detail}"


class Page:
    def __init__(self, session, context, contexts, options):
        self.session = session
        self.context = context
        self.contexts = contexts
        self.options = options
        self.value = options.value

    def call(self, method, params=None, timeout=COMMAND_TIMEOUT):
        return self.session.call(method, params, timeout)

    def evaluate(self, expression):
        result = self.call("script.evaluate", {"expression": expression, "target": {"context": self.context},
                                               "awaitPromise": True})
        return checked(result)["result"]

    def apply(self, function, shared_id):
        result = self.call("script.callFunction", {"functionDeclaration": function, "awaitPromise": False,
                                                   "arguments": [{"sharedId": shared_id}],
                                                   "target": {"context": self.context}})
        return plain(checked(result)["result"])


def checked(result):
    if result.get("type") == EXCEPTION:
        raise RuntimeError(SCRIPT_FAILED.format(detail=result["exceptionDetails"].get("text")))
    return result


def plain(remote):
    kind, value = remote.get("type"), remote.get("value")
    if kind in ("array", "set"):
        return [plain(item) for item in value or []]
    if kind in ("object", "map"):
        return {key if isinstance(key, str) else str(plain(key)): plain(item) for key, item in value or []}
    return kind if value is None else value


def locator_kind(selector):
    return XPATH if selector.lstrip().startswith(XPATH_START) else CSS


def locator(selector, kind=None):
    return {"type": kind or locator_kind(selector), "value": selector}


def nodes(page, selector, kind=None, limit=1):
    params = {"context": page.context, "locator": locator(selector, kind), "maxNodeCount": limit}
    return page.call("browsingContext.locateNodes", params).get("nodes", [])


def shared_id_of(page, selector, kind=None):
    found = nodes(page, selector, kind)
    if not found:
        raise LookupError(f"element not found: {selector}")
    return found[0]["sharedId"]


def tree(page):
    return page.call("browsingContext.getTree")["contexts"]


def flatten(contexts):
    for entry in contexts:
        yield entry
        yield from flatten(entry.get("children") or [])


def url_of(page, context=None):
    wanted = context or page.context
    return next((entry["url"] for entry in flatten(tree(page)) if entry["context"] == wanted), "")


def index_of(contexts, context):
    return next((index for index, entry in enumerate(contexts) if entry["context"] == context), -1)


def stdin_text():
    return sys.stdin.buffer.read().decode("utf-8", errors="replace").rstrip("\r\n")
