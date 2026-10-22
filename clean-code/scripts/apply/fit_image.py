import argparse
import io
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "lib"))

from common import guard
from runs import load_config, project_root

BOX = re.compile(r"^(?P<width>\d+)x(?P<height>\d+)(?::(?P<below>\d+))?$")
DENSITIES = (1, 2)
KILO = 1024
CENTER = 0.5
EFFORT = 6
DIGITS = 2
VECTOR = ".svg"
FOCUS_HINT = "focus reads X,Y with both between 0 and 1"


def box(text):
    match = BOX.match(text)
    if not match or not int(match.group("width")) or not int(match.group("height")):
        raise argparse.ArgumentTypeError("a box reads WIDTHxHEIGHT, or WIDTHxHEIGHT:MAXVIEWPORT")
    width, height, below = match.groups()
    return int(width), int(height), int(below) if below else None


def focus(text):
    try:
        x, y = (float(part) for part in text.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError(FOCUS_HINT) from None
    if not (0 <= x <= 1 and 0 <= y <= 1):
        raise argparse.ArgumentTypeError(FOCUS_HINT)
    return x, y


def _pillow():
    try:
        from PIL import Image, ImageOps, features
    except ImportError:
        raise RuntimeError("Pillow is missing: python -m pip install --user pillow") from None
    if not features.check("webp"):
        raise RuntimeError("this Pillow has no WebP encoder, reinstall it from the official wheel")
    return Image, ImageOps


def crop(size, aspect, point):
    width, height = size
    wide = width / height < aspect
    crop_width, crop_height = (width, round(width / aspect)) if wide else (round(height * aspect), height)
    left = min(max(round(point[0] * width - crop_width * CENTER), 0), width - crop_width)
    top = min(max(round(point[1] * height - crop_height * CENTER), 0), height - crop_height)
    return left, top, left + crop_width, top + crop_height


def _encoded(image, quality):
    best = None
    modes = ((f"quality {quality}", {"quality": quality, "method": EFFORT}), ("lossless", {"lossless": True}))
    for mode, options in modes:
        buffer = io.BytesIO()
        image.save(buffer, "WEBP", **options)
        if best is None or buffer.tell() < len(best[1]):
            best = mode, buffer.getvalue()
    return best


def render(image, wanted, args, quality):
    Image, _ = _pillow()
    width, height, _ = wanted
    framed = image.crop(crop(image.size, width / height, args.focus))
    made = []
    for density in DENSITIES:
        scale = min(density, framed.width / width)
        size = (round(width * scale), round(height * scale))
        if made and made[-1][1] == size:
            continue
        if scale < density:
            print(f"source too small for {density}x of {width}x{height}, kept at {size[0]}x{size[1]}")
        mode, data = _encoded(framed.resize(size, Image.LANCZOS), quality)
        path = args.out / f"{args.image.stem}-{size[0]}x{size[1]}.webp"
        path.write_bytes(data)
        made.append((path, size, round(scale, DIGITS), mode))
    return made


def _srcset(made, prefix):
    return ", ".join(f"{prefix}{path.name} {density:g}x" for path, _, density, _ in made)


def snippet(results, prefix):
    fallback = ([pair for pair in results if pair[0][2] is None] or results)[-1]
    (width, height, _), made = fallback
    img = (f'<img src="{prefix}{made[0][0].name}" srcset="{_srcset(made, prefix)}" '
           f'width="{width}" height="{height}" alt="">')
    sources = [f'  <source media="(max-width: {wanted[2]}px)" srcset="{_srcset(made, prefix)}">'
               for wanted, made in sorted(results, key=lambda pair: pair[0][2] or 0) if wanted[2]]
    return "\n".join(["<picture>", *sources, f"  {img}", "</picture>"]) if sources else img


def main():
    parser = argparse.ArgumentParser(description="Crop an image to its display box and write 1x and 2x WebP files.")
    parser.add_argument("image", type=Path)
    parser.add_argument("--box", type=box, action="append", required=True, help="WIDTHxHEIGHT[:MAXVIEWPORT]")
    parser.add_argument("--focus", type=focus, default=(CENTER, CENTER), help="X,Y kept in frame, 0 to 1")
    parser.add_argument("--out", type=Path, help="folder for the WebP files, defaults to the image folder")
    parser.add_argument("--prefix", default="", help="URL folder written before each file name in the snippet")
    parser.add_argument("--quality", type=int, help="WebP quality, defaults to webp_quality of the config")
    args = parser.parse_args()
    args.image = args.image.resolve()
    if args.image.suffix.lower() == VECTOR:
        raise ValueError("an SVG stays SVG: scale it in the markup, never rasterise it")
    args.out = (args.out or args.image.parent).resolve()
    args.out.mkdir(parents=True, exist_ok=True)
    quality = args.quality or load_config(project_root(args.image))["webp_quality"]
    Image, ImageOps = _pillow()
    with Image.open(args.image) as opened:
        image = ImageOps.exif_transpose(opened)
        image = image.convert("RGBA" if "A" in image.getbands() or "transparency" in image.info else "RGB")
    before = args.image.stat().st_size
    print(f"{args.image.name}: {image.width}x{image.height}, {before // KILO} KB")
    results = [(wanted, render(image, wanted, args, quality)) for wanted in args.box]
    for _, made in results:
        for path, size, density, mode in made:
            weight = path.stat().st_size
            heavier = ", heavier than the source: keep the source or lower the quality" if weight > before else ""
            print(f"{path.name}: {size[0]}x{size[1]} at {density:g}x, {mode}, {weight // KILO} KB{heavier}")
    print(snippet(results, args.prefix.rstrip("/") + "/" if args.prefix else ""))


if __name__ == "__main__":
    guard(main, "crop the image to the box ratio in an editor, export it at 1x and 2x as WebP, quality 80")
