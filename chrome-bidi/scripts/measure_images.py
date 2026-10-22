import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.browser import NAV_TIMEOUT, first_context, throwaway
from actions.shared import checked
from core.common import LOCALHOST, guard
from core.target import Target

DEFAULT_WIDTHS = "390,1440"
VIEW_HEIGHT = 720
SELECTOR_DEPTH = 4
LOAD_WAIT_MS = 5000
DATA_URL_KEEP = 60
MEASURE = r"""async (depth, wait, keep) => {
  const round = value => Math.round(value * 100) / 100;
  const total = (style, names) => names.reduce((sum, name) => sum + (parseFloat(style[name]) || 0), 0);
  const box = (element, withPadding) => {
    const rect = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    const across = ['borderLeftWidth', 'borderRightWidth'].concat(withPadding ? [] : ['paddingLeft', 'paddingRight']);
    const down = ['borderTopWidth', 'borderBottomWidth'].concat(withPadding ? [] : ['paddingTop', 'paddingBottom']);
    return [round(rect.width - total(style, across)), round(rect.height - total(style, down))];
  };
  const step = element => {
    if (element.id) return element.localName + '#' + CSS.escape(element.id);
    const first = element.classList[0];
    const siblings = element.parentElement ? [...element.parentElement.children] : [];
    const twins = siblings.filter(child => child.localName === element.localName);
    const order = twins.length > 1 ? ':nth-of-type(' + (twins.indexOf(element) + 1) + ')' : '';
    return element.localName + (first ? '.' + CSS.escape(first) : '') + order;
  };
  const path = element => {
    const parts = [];
    for (let current = element; current && current.nodeType === 1 && parts.length < depth;
         current = current.parentElement) {
      parts.unshift(step(current));
      if (current.id) break;
    }
    return parts.join(' > ');
  };
  const short = src => src.startsWith('data:') ? src.slice(0, keep) : src;
  const settle = image => image.complete ? null : new Promise(done => {
    image.addEventListener('load', done, {once: true});
    image.addEventListener('error', done, {once: true});
    setTimeout(done, wait);
  });
  const sizes = new Map();
  const natural = src => {
    if (!sizes.has(src)) sizes.set(src, new Promise(done => {
      const probe = new Image();
      const timer = setTimeout(() => done([0, 0]), wait);
      probe.onload = () => { clearTimeout(timer); done([probe.naturalWidth, probe.naturalHeight]); };
      probe.onerror = () => { clearTimeout(timer); done([0, 0]); };
      probe.src = src;
    }));
    return sizes.get(src);
  };
  const images = [...document.images];
  images.forEach(image => { if (image.loading === 'lazy') image.loading = 'eager'; });
  await Promise.all(images.map(settle));
  const found = [];
  for (const image of images) {
    const size = box(image, false);
    if (size[0] <= 0 || size[1] <= 0) continue;
    found.push({src: short(image.currentSrc || image.src), kind: 'img', box: size,
      natural: [image.naturalWidth, image.naturalHeight], fit: getComputedStyle(image).objectFit,
      selector: path(image)});
  }
  for (const element of document.querySelectorAll('*')) {
    const style = getComputedStyle(element);
    if (style.backgroundImage === 'none') continue;
    const size = box(element, true);
    if (size[0] <= 0 || size[1] <= 0) continue;
    for (const match of style.backgroundImage.matchAll(/url\("((?:[^"\\]|\\.)*)"\)/g)) {
      found.push({src: short(match[1]), kind: 'background', box: size, natural: await natural(match[1]),
        fit: style.backgroundSize, selector: path(element)});
    }
  }
  return JSON.stringify({dpr: devicePixelRatio, images: found});
}"""


def widths_of(text):
    return [int(part) for part in text.split(",") if part.strip()]


def measure_width(session, context, url, size):
    width, height = size
    session.call("browsingContext.setViewport", {"context": context, "viewport": {"width": width, "height": height}})
    session.call("browsingContext.navigate", {"context": context, "url": url, "wait": "complete"}, NAV_TIMEOUT)
    arguments = [{"type": "number", "value": value} for value in (SELECTOR_DEPTH, LOAD_WAIT_MS, DATA_URL_KEEP)]
    result = session.call("script.callFunction", {"functionDeclaration": MEASURE, "arguments": arguments,
                                                  "target": {"context": context}, "awaitPromise": True}, NAV_TIMEOUT)
    page = json.loads(checked(result)["result"]["value"])
    return [{"width": width, "dpr": page["dpr"], **image} for image in page["images"]]


def main():
    parser = argparse.ArgumentParser(description="Measure the box of every displayed image, one pass per width.")
    parser.add_argument("--url", required=True, help="page url, or a local file or folder served on " + LOCALHOST)
    parser.add_argument("--widths", type=widths_of, default=widths_of(DEFAULT_WIDTHS))
    parser.add_argument("--height", type=int, default=VIEW_HEIGHT)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--visible", action="store_true", help="show the window, only when the user asked to watch")
    parser.add_argument("--desktop", help="with --visible: virtual desktop index, or 'current'")
    options = parser.parse_args()
    with Target(options.url) as target, throwaway(visible=options.visible, desktop_choice=options.desktop) as session:
        context = first_context(session)
        records = [record for width in options.widths
                   for record in measure_width(session, context, target.url, (width, options.height))]
    options.out.parent.mkdir(parents=True, exist_ok=True)
    options.out.write_text(json.dumps(records, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{len(records)} image boxes at widths {options.widths}, written to {options.out}")


if __name__ == "__main__":
    guard(main, "open the page in Chrome, set each width with browsingContext.setViewport, and read "
                "getBoundingClientRect, naturalWidth and the computed background-image of each element")
