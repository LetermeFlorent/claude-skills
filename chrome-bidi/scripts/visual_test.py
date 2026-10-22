import argparse
import base64
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from actions.capture import save_screenshot
from core.browser import throwaway
from core.common import guard
from core.target import Target, run_dir
from measure_images import DEFAULT_WIDTHS, VIEW_HEIGHT, first_context, measure_width, widths_of

HEAVY_RATIO = 2
SHOWN_LIMIT = 20


def verdict(record):
    needed = record["box"][0] * record["dpr"]
    if not record["natural"][0]:
        return "not loaded"
    ratio = record["natural"][0] / needed
    if ratio < 1:
        return f"blurry, file {ratio:.2f}x of the box"
    return f"heavy, file {ratio:.2f}x of the box" if ratio > HEAVY_RATIO else None


def report(records, json_path):
    flagged = [(record, note) for record in records if (note := verdict(record))]
    print(f"images: {len(records)} boxes measured, {len(flagged)} to look at, details in {json_path}")
    for record, note in flagged[:SHOWN_LIMIT]:
        print(f"  {record['width']}px {record['kind']} {record['selector']}: box {record['box']}, "
              f"file {record['natural']}, {note}")
    if len(flagged) > SHOWN_LIMIT:
        print(f"  {len(flagged) - SHOWN_LIMIT} more in the json")


def main():
    parser = argparse.ArgumentParser(description="Screenshot a page at several widths and measure its images.")
    parser.add_argument("target", help="page url, or a local folder or file served on 127.0.0.1")
    parser.add_argument("widths", nargs="?", type=widths_of, default=widths_of(DEFAULT_WIDTHS))
    parser.add_argument("--height", type=int, default=VIEW_HEIGHT)
    parser.add_argument("--visible", action="store_true", help="show the window, only when the user asked to watch")
    parser.add_argument("--desktop", help="with --visible: virtual desktop index, or 'current'")
    options = parser.parse_args()
    records = []
    with Target(options.target) as target:
        run = run_dir(target.root)
        print(f"page: {target.url}")
        with throwaway(visible=options.visible, desktop_choice=options.desktop) as session:
            context = first_context(session)
            for width in options.widths:
                records += measure_width(session, context, target.url, (width, options.height))
                data = session.call("browsingContext.captureScreenshot", {"context": context})["data"]
                shot = run / f"shot-{width}.png"
                factor = save_screenshot(base64.b64decode(data), shot)
                print(f"shot {width}px: {shot}" + (f" (scaled down {factor:.3f})" if factor != 1.0 else ""))
    json_path = run / "images.json"
    json_path.write_text(json.dumps(records, indent=1, ensure_ascii=False), encoding="utf-8")
    report(records, json_path)


if __name__ == "__main__":
    guard(main, "run launch.py, then bidi.py viewport <width>x720, nav <url> and shot <file> for each width, "
                "then measure_images.py, then bidi.py close")
