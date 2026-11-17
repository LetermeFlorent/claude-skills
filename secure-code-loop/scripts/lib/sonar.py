import base64
import json
import os
import re
import shutil
import urllib.parse
import urllib.request

from common import ENCODING, last_line, run, write_json
from parsers import LOW, SECURITY_QUALITIES, Raw, level, most_severe

DEFAULT_URL = "http://localhost:9000"
LOOPBACK = frozenset({"localhost", "127.0.0.1", "::1"})
SCANNER_WORK = ".scannerwork"
GATE_FAILED = "QUALITY GATE STATUS: FAILED"
STATUS_UP = "UP"
PAGE_SIZE = 500
PAGE_LIMIT = 20
HTTP_TIMEOUT = 30
KEY_CHARACTERS = re.compile(r"[^\w.:-]")
LOCAL_ONLY = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def fetch(url, path, query):
    token = base64.b64encode(f"{os.environ.get('SONAR_TOKEN', '')}:".encode(ENCODING)).decode(ENCODING)
    address = f"{url}{path}?{urllib.parse.urlencode(query)}" if query else f"{url}{path}"
    request = urllib.request.Request(address, headers={"Authorization": f"Basic {token}"})
    try:
        with LOCAL_ONLY.open(request, timeout=HTTP_TIMEOUT) as answer:
            return json.loads(answer.read().decode(ENCODING))
    except (OSError, ValueError):
        return None


def server():
    url = os.environ.get("SONAR_HOST_URL", DEFAULT_URL).rstrip("/")
    host = urllib.parse.urlparse(url).hostname
    if host not in LOOPBACK:
        return url, f"skipped: {host} is not this machine, the user runs it on their own server"
    if not os.environ.get("SONAR_TOKEN"):
        return url, "skipped: SONAR_TOKEN is not set"
    status = fetch(url, "/api/system/status", {})
    if not status or status.get("status") != STATUS_UP:
        return url, f"skipped: no server up at {url}"
    return url, None


def pages(url, path, query, field):
    items = []
    for page in range(1, PAGE_LIMIT + 1):
        data = fetch(url, path, {**query, "ps": PAGE_SIZE, "p": page})
        if data is None:
            return None
        items += data.get(field) or []
        if not data.get(field) or len(items) >= (data.get("paging") or {}).get("total", 0):
            break
    return items


def analyse(root, output, timeout):
    url, why = server()
    if why:
        return why
    key = os.environ.get("SONAR_PROJECT_KEY") or KEY_CHARACTERS.sub("-", root.name)
    work = root / SCANNER_WORK
    existed = work.exists()
    code, out, err = run(["sonar-scanner", f"-Dsonar.projectKey={key}", "-Dsonar.qualitygate.wait=true"], root,
                         timeout, {"SONAR_HOST_URL": url})
    if not existed:
        shutil.rmtree(work, ignore_errors=True)
    if code is None or (code != 0 and GATE_FAILED not in out):
        return f"failed: {last_line(err or out)}"
    issues = pages(url, "/api/issues/search", {"components": key, "resolved": "false"}, "issues")
    hotspots = pages(url, "/api/hotspots/search", {"project": key, "status": "TO_REVIEW"}, "hotspots")
    if issues is None or hotspots is None:
        return f"failed: {url} did not return the issues of {key}"
    write_json(output, {"key": key, "issues": issues, "hotspots": hotspots})
    return None


def component_path(component, key):
    prefix = f"{key}:"
    return component[len(prefix):] if component.startswith(prefix) else component.partition(":")[2] or component


def issue_level(item):
    impacts = item.get("impacts")
    if impacts:
        return most_severe([level(impact.get("severity")) for impact in impacts
                            if impact.get("softwareQuality") in SECURITY_QUALITIES])
    return LOW if item.get("type") == "CODE_SMELL" else level(item.get("severity"))


def parse(data, place):
    key = data.get("key", "")
    found = [Raw("sonar", item.get("rule", ""), issue_level(item), component_path(item.get("component", ""), key),
                 item.get("line", 0), item.get("message", ""), item.get("rule")) for item in data.get("issues") or []]
    return found + [Raw("sonar", item.get("ruleKey", ""), level(item.get("vulnerabilityProbability")),
                        component_path(item.get("component", ""), key), item.get("line", 0),
                        item.get("message", ""), item.get("ruleKey")) for item in data.get("hotspots") or []]
