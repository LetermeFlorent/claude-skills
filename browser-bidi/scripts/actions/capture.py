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
MAX_SHOT_WIDTH = 1024
MAX_SHOT_HEIGHT = 720


def scale_of(width, height, max_height=MAX_SHOT_HEIGHT):
    return max(1.0, width / MAX_SHOT_WIDTH, height / max_height if max_height else 0)


def save_screenshot(data, target, max_height=MAX_SHOT_HEIGHT):
    target = Path(target).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    width, height = struct.unpack(">II", data[16:24])
    factor = scale_of(width, height, max_height)
    if factor == 1.0:
        target.write_bytes(data)
        return factor
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=WORK_DIR) as scratch:
        source = Path(scratch) / "full.png"
        source.write_bytes(data)
        quote = lambda path: str(path).replace("'", "''")
        powershell(RESIZE.format(source=quote(source), target=quote(target), width=round(width / factor),
                                 height=round(height / factor)))
    return factor


def capture(page, params):
    return base64.b64decode(page.call("browsingContext.captureScreenshot", {"context": page.context, **params})["data"])


def scaled(factor):
    return f" (scaled down, multiply coordinates by {factor:.3f})" if factor != 1.0 else ""


def shot(page):
    print(f"screenshot: {page.value}" + scaled(save_screenshot(capture(page, {}), page.value)))


def fullshot(page):
    factor = save_screenshot(capture(page, {"origin": "document"}), page.value, None)
    print(f"full page screenshot: {page.value}" + scaled(factor))


def elementshot(page):
    selector, file = split_value(page.value, 2)
    clip = {"type": "element", "element": {"sharedId": shared_id_of(page, selector)}}
    factor = save_screenshot(capture(page, {"clip": clip}), file, None)
    print(f"screenshot of {selector}: {file}" + scaled(factor))


def pdf(page):
    data = page.call("browsingContext.print", {"context": page.context, "background": True})["data"]
    Path(page.value).write_bytes(base64.b64decode(data))
    print(f"pdf: {page.value}")


ACTIONS = {"shot": shot, "fullshot": fullshot, "elementshot": elementshot, "pdf": pdf}
