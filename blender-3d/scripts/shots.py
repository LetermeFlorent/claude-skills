import argparse
import sys
sys.dont_write_bytecode = True
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from blender import existing, guard, launch, refuse, report

HINT = "set a camera, scene.render.filepath, then bpy.ops.render.render(write_still=True)"
VIEWS = "front,side,top,three_quarter"


def parse(argv):
    parser = argparse.ArgumentParser(description="Render captures framing every object; the file is never saved.")
    parser.add_argument("source", help=".blend or any importable model file")
    parser.add_argument("out_dir", help="folder for the PNG files")
    parser.add_argument("--engine", default="workbench", help="workbench, eevee, cycles or any engine id")
    parser.add_argument("--views", default=VIEWS, help="comma list: front back left right side top bottom "
                        "three_quarter, or elevation:azimuth in degrees")
    parser.add_argument("--size", type=int, default=768)
    parser.add_argument("--zoom", type=float, default=1.0, help="closer camera for texture detail, e.g. 4")
    parser.add_argument("--prefix", default="", help="file name start, e.g. 03-")
    parser.add_argument("--timeout", type=int, default=900)
    return parser.parse_args(argv)


def main():
    options = parse(sys.argv[1:])
    problems = []
    source = existing(options.source, problems, "source")
    if not 16 <= options.size <= 8192:
        problems.append(f"--size out of 16..8192: {options.size}")
    if not 1 <= options.zoom <= 50:
        problems.append(f"--zoom out of 1..50: {options.zoom}")
    if problems or source == "-":
        refuse(problems or ["give a file to capture"])
    out_dir = str(Path(options.out_dir).resolve())
    rest = [source, out_dir, options.engine, options.views, options.size, options.prefix, options.zoom]
    report(*launch(source, "shots_bl.py", rest, options.timeout))
    print("next: open every PNG above with the image tool and compare it with the checklist")


if __name__ == "__main__":
    guard(main, HINT)
