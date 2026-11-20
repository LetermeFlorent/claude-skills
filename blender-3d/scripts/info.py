import argparse
import sys
sys.dont_write_bytecode = True
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from blender import existing, guard, launch, refuse, report

HINT = "open the file in Blender and read the Statistics overlay and the Outliner"


def main():
    parser = argparse.ArgumentParser(description="Print objects, mesh counts, materials, images, actions.")
    parser.add_argument("source", help=".blend or any importable model file (.glb, .fbx, .obj, ...)")
    parser.add_argument("--timeout", type=int, default=300)
    options = parser.parse_args()
    problems = []
    source = existing(options.source, problems, "source")
    if problems or source == "-":
        refuse(problems or ["give a file to inspect"])
    report(*launch(source, "inspect_bl.py", [source], options.timeout))


if __name__ == "__main__":
    guard(main, HINT)
