import re
from collections import defaultdict
from pathlib import PurePosixPath
from urllib.parse import parse_qs, unquote, urlparse

from pictures import dimensions

DEAD_RULE = 3
IMAGE_RULE = 19
RASTER = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp", ".avif"}
WEB = {".webp", ".avif"}
EXEMPT = re.compile(r"favicon|apple-touch|mstile|android-chrome|og[-_.]|opengraph|twitter-card", re.IGNORECASE)
REFERENCE = re.compile(r"[\w@./%-]+\.(?:png|jpe?g|gif|bmp|tiff?|webp|avif|svg)\b", re.IGNORECASE)
SIZE = re.compile(r"\b(width|height)\s*[=:]\s*[{\"']?\s*(\d+)")
RESPONSIVE = re.compile(r"srcset|sizes=|<picture|next/image|<Image\b|image-set\(", re.IGNORECASE)
TAG = re.compile(r"<img\b", re.IGNORECASE)
KILO = 1024
DENSITY = 2
TOLERANCE = 0.1
RATIO_GAP = 0.02
CONTEXT_LINES = 3
SHOWN = 3


def _name(url):
    parsed = urlparse(url)
    inner = parse_qs(parsed.query).get("url")
    return PurePosixPath(unquote(urlparse(inner[0]).path if inner else parsed.path)).name


def _reference(item, number, line):
    near = " ".join(item["lines"][max(0, number - CONTEXT_LINES):number + CONTEXT_LINES])
    sizes = dict((key, int(value)) for key, value in SIZE.findall(near))
    return {"at": f"{item['rel']}:{number}", "tag": bool(TAG.search(line)), "responsive": bool(RESPONSIVE.search(near)),
            "sizes": sizes}


def _references(files, names):
    found = defaultdict(list)
    for item in files:
        if not (item["code"] or item["prose"]) or item["data"]:
            continue
        for number, line in enumerate(item["lines"], 1):
            for name in sorted({_name(match.group(0)) for match in REFERENCE.finditer(line)} & names):
                found[name].append(_reference(item, number, line))
    return found


def _boxes(config):
    largest = defaultdict(lambda: [0, 0])
    for shown in config.get("boxes", []):
        box, name = shown.get("box", [0, 0]), _name(shown.get("src", ""))
        if box[0] > largest[name][0]:
            largest[name] = [box[0], box[1]]
    return largest


def _weight_problems(item, natural, config):
    suffix, weight = item["path"].suffix.lower(), item["path"].stat().st_size
    problems = []
    if suffix in RASTER and suffix not in WEB and not EXEMPT.search(item["rel"]):
        problems.append(f"{suffix[1:].upper()} not WebP")
    pixels = natural[0] * natural[1] if natural else 0
    if weight > config["max_image_kb"] * KILO or (pixels and weight / pixels > config["max_bytes_per_pixel"]):
        problems.append(f"{weight // KILO} KB" + (f", {weight / pixels:.2f} bytes per pixel" if pixels else ""))
    return problems


def _fit_problems(natural, refs, live):
    declared = [[ref["sizes"].get("width", 0), ref["sizes"].get("height", 0)] for ref in refs]
    box = live or max(declared, key=lambda size: size[0], default=[0, 0])
    if not natural or not box[0]:
        return []
    problems, needed = [], box[0] * DENSITY
    if natural[0] > needed * (1 + TOLERANCE):
        problems.append(f"{natural[0]}x{natural[1]} for a {box[0]}x{box[1] or '?'} box, 2x needs {needed} wide")
    if box[1] and abs(natural[0] / natural[1] - box[0] / box[1]) > RATIO_GAP * box[0] / box[1]:
        problems.append(f"ratio {natural[0] / natural[1]:.2f} in a {box[0] / box[1]:.2f} box, crop it")
    return problems


def _tag_problems(suffix, refs):
    tags = [ref for ref in refs if ref["tag"]]
    problems = ["img without width and height"] if any(not ref["sizes"] for ref in tags) else []
    if suffix in RASTER and any(not ref["responsive"] for ref in tags):
        problems.append("img without a 1x and 2x srcset")
    return problems


def check(files, root, config):
    images = [item for item in files if item.get("image") and not item["data"]]
    refs, live = _references(files, {item["path"].name for item in images}), _boxes(config)
    findings, weight = [], 0
    for item in images:
        weight += item["path"].stat().st_size
        name, natural = item["path"].name, dimensions(item["path"])
        if not refs[name] and not live.get(name):
            if not EXEMPT.search(item["rel"]):
                findings.append({"rule": DEAD_RULE, "file": item["rel"], "line": 0, "what": "image never referenced",
                                 "proof": "its name appears in no code or prose file"})
            continue
        problems = (_weight_problems(item, natural, config) + _fit_problems(natural, refs[name], live.get(name))
                    + _tag_problems(item["path"].suffix.lower(), refs[name]))
        if problems:
            where = ", ".join(ref["at"] for ref in refs[name][:SHOWN]) or "the measured page"
            findings.append({"rule": IMAGE_RULE, "file": item["rel"], "line": 0, "what": "; ".join(problems),
                             "proof": f"{natural[0]}x{natural[1]} px, used at {where}" if natural else where})
    return findings, {"images": len(images), "image_kb": weight // KILO, "live_boxes": bool(live)}
