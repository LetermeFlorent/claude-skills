import base64
import struct
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

from core.common import WORK_DIR, split_value
from actions.page import shared_id_of
from core.processes import powershell


RESIZE = ("Add-Type -AssemblyName System.Drawing; $source = [Drawing.Image]::FromFile('{source}'); "
          "$target = New-Object Drawing.Bitmap {width}, {height}; $pen = [Drawing.Graphics]::FromImage($target); "
          "$pen.InterpolationMode = 'HighQualityBicubic'; $pen.DrawImage($source, 0, 0, {width}, {height}); "
          "$pen.Dispose(); $source.Dispose(); $target.Save('{target}', [Drawing.Imaging.ImageFormat]::Png); "
          "$target.Dispose()")
MAX_SHOT_HEIGHT = 720


def save_screenshot(data, target, max_height=MAX_SHOT_HEIGHT):
    target = Path(target).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    width, height = struct.unpack(">II", data[16:24])
    if height <= max_height:
        target.write_bytes(data)
        return 1.0
    factor = height / max_height
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=WORK_DIR) as scratch:
        source = Path(scratch) / "full.png"
        source.write_bytes(data)
        quote = lambda path: str(path).replace("'", "''")
        powershell(RESIZE.format(source=quote(source), target=quote(target), width=round(width / factor),
                                 height=max_height))
    return factor


def capture(page, params):
    return base64.b64decode(page.call("browsingContext.captureScreenshot", {"context": page.context, **params})["data"])


def shot(page):
    factor = save_screenshot(capture(page, {}), page.value)
    scaled = f" (scaled to {MAX_SHOT_HEIGHT}p, multiply coordinates by {factor:.3f})"
    print(f"screenshot: {page.value}" + (scaled if factor != 1.0 else ""))


def fullshot(page):
    Path(page.value).write_bytes(capture(page, {"origin": "document"}))
    print(f"full page screenshot: {page.value}")


def elementshot(page):
    selector, file = split_value(page.value, 2)
    clip = {"type": "element", "element": {"sharedId": shared_id_of(page, selector)}}
    Path(file).write_bytes(capture(page, {"clip": clip}))
    print(f"screenshot of {selector}: {file}")


def pdf(page):
    data = page.call("browsingContext.print", {"context": page.context, "background": True})["data"]
    Path(page.value).write_bytes(base64.b64decode(data))
    print(f"pdf: {page.value}")


ACTIONS = {"shot": shot, "fullshot": fullshot, "elementshot": elementshot, "pdf": pdf}
