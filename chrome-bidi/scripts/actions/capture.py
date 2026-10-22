import base64
import struct
import tempfile
from pathlib import Path

from actions.shared import PAIR, shared_id_of
from core.common import WORK_DIR, split_value
from core.processes import powershell

MAX_SHOT_HEIGHT = 720
PNG_SIZE_SLICE = slice(16, 24)
RESIZE = ("Add-Type -AssemblyName System.Drawing; $source = [Drawing.Image]::FromFile('{source}'); "
          "$target = New-Object Drawing.Bitmap {width}, {height}; $pen = [Drawing.Graphics]::FromImage($target); "
          "$pen.InterpolationMode = 'HighQualityBicubic'; $pen.DrawImage($source, 0, 0, {width}, {height}); "
          "$pen.Dispose(); $source.Dispose(); $target.Save('{target}', [Drawing.Imaging.ImageFormat]::Png); "
          "$target.Dispose()")


def quoted(path):
    return str(path).replace("'", "''")


def png_size(data):
    return struct.unpack(">II", data[PNG_SIZE_SLICE])


def save_screenshot(data, target, max_height=MAX_SHOT_HEIGHT):
    target = Path(target).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    width, height = png_size(data)
    if height <= max_height:
        target.write_bytes(data)
        return 1.0
    factor = height / max_height
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=WORK_DIR) as scratch:
        source = Path(scratch) / "full.png"
        source.write_bytes(data)
        powershell(RESIZE.format(source=quoted(source), target=quoted(target), width=round(width / factor),
                                 height=max_height))
    return factor


def capture(page, params):
    return base64.b64decode(page.call("browsingContext.captureScreenshot", {"context": page.context, **params})["data"])


def shot(page):
    factor = save_screenshot(capture(page, {}), page.value)
    if factor == 1.0:
        print(f"screenshot: {page.value}")
    else:
        print(f"screenshot: {page.value} (scaled to {MAX_SHOT_HEIGHT}p, multiply coordinates by {factor:.3f})")


def fullshot(page):
    Path(page.value).write_bytes(capture(page, {"origin": "document"}))
    print(f"full page screenshot: {page.value}")


def elementshot(page):
    selector, file = split_value(page.value, PAIR)
    clip = {"type": "element", "element": {"sharedId": shared_id_of(page, selector)}}
    Path(file).write_bytes(capture(page, {"clip": clip}))
    print(f"screenshot of {selector}: {file}")


def pdf(page):
    data = page.call("browsingContext.print", {"context": page.context, "background": True})["data"]
    Path(page.value).write_bytes(base64.b64decode(data))
    print(f"pdf: {page.value}")


ACTIONS = {"shot": shot, "fullshot": fullshot, "elementshot": elementshot, "pdf": pdf}
