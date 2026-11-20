import json
import re
import tempfile
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from blender import run

SITE = {"manual": "https://docs.blender.org/manual/en/{}/", "api": "https://docs.blender.org/api/{}/"}
CACHE = Path(tempfile.gettempdir()) / "blender-docs"
AGENT = "blender-3d-skill"
TIMEOUT = 60
MIN_STEM = 4
CONTEXT = 4
SKIPPED = {"script", "style", "nav", "aside", "footer", "header"}
BLOCKS = {"p", "li", "h1", "h2", "h3", "h4", "pre", "dt", "dd", "tr", "div", "section", "br"}


def version(exe):
    code, output = run([exe, "--version"], TIMEOUT)
    found = re.search(r"Blender (\d+\.\d+)", output or "")
    return found.group(1) if code == 0 and found else ""


def base_url(docs, release):
    return SITE[docs].format(release)


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read().decode("utf-8", errors="replace")


def index(root):
    CACHE.mkdir(exist_ok=True)
    cached = CACHE / (re.sub(r"[^\w.]+", "_", root.split("//")[1]) + "searchindex.js")
    if not cached.exists():
        cached.write_text(fetch(root + "searchindex.js"), encoding="utf-8")
    text = cached.read_text(encoding="utf-8")
    return json.loads(text[text.index("(") + 1:text.rindex(")")])


def pages_for(table, word):
    for size in range(len(word), min(len(word), MIN_STEM) - 1, -1):
        hit = table.get(word[:size], table.get(word[:size] + "e"))
        if hit is not None:
            return set(hit) if isinstance(hit, list) else {hit}
    return set()


def search(data, query):
    words = [w for w in re.split(r"[^a-z0-9]+", query.lower()) if w]
    scores = {}
    for word in words:
        in_titles = pages_for(data["titleterms"], word)
        in_text = pages_for(data["terms"], word)
        for page in in_titles | in_text:
            matched, points = scores.get(page, (0, 0))
            title_hit = word[:max(MIN_STEM - 1, len(word) - 3)] in data["titles"][page].lower()
            scores[page] = (matched + 1, points + 5 * (page in in_titles) + 3 * title_hit + 1)
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return [(score, data["titles"][page], data["docnames"][page] + ".html") for page, score in ranked]


class Article(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside, self.skip, self.parts = 0, 0, []

    def handle_starttag(self, tag, attrs):
        if tag in ("article", "main") or dict(attrs).get("role") == "main":
            self.inside += 1
        self.skip += tag in SKIPPED
        if tag in BLOCKS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        self.skip -= tag in SKIPPED and self.skip > 0
        if tag in BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.inside and not self.skip:
            self.parts.append(data)


def page_text(url):
    reader = Article()
    reader.feed(fetch(url))
    lines = (" ".join(line.split()) for line in "".join(reader.parts).splitlines())
    return "\n".join(line.replace("\u00b6", "") for line in lines if line)


def find_lines(text, word):
    lines = text.splitlines()
    keep = set()
    for number, line in enumerate(lines):
        if word.lower() in line.lower():
            keep.update(range(max(0, number - CONTEXT), min(len(lines), number + CONTEXT + 1)))
    shown, last = [], None
    for number in sorted(keep):
        if last is not None and number != last + 1:
            shown.append("...")
        shown.append(lines[number])
        last = number
    return shown
