import argparse
import sys
sys.dont_write_bytecode = True
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from blender import guard, launch, report

HINT = "blender --background --python-expr \"import bpy; print(bpy.ops.mesh.bevel.get_rna_type().properties.keys())\""


def main():
    parser = argparse.ArgumentParser(description="Read operators, types and nodes from the installed Blender.")
    parser.add_argument("query", nargs="?", default="",
                        help="empty: version only; bpy.ops.x.y, a bpy.types name, a node type, or a word")
    parser.add_argument("--timeout", type=int, default=300)
    options = parser.parse_args()
    report(*launch("-", "api_bl.py", [options.query], options.timeout))


if __name__ == "__main__":
    guard(main, HINT)
