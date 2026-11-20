import argparse
import sys
sys.dont_write_bytecode = True
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from blender import existing, guard, launch, refuse, report

HINT = "blender --background <file.blend> --python-exit-code 1 --python <script.py>"


def parse(argv):
    parser = argparse.ArgumentParser(description="Run any bpy script in Blender, headless.")
    parser.add_argument("source", help=".blend, any importable model file, or - for an empty scene")
    parser.add_argument("script", help="bpy script to run")
    parser.add_argument("--save", default="", help="new .blend to write after the script, never the source")
    parser.add_argument("--timeout", type=int, default=900)
    return parser.parse_args(argv)


def check(options):
    problems = []
    source = existing(options.source, problems, "source")
    script = existing(options.script, problems, "script")
    save = str(Path(options.save).resolve()) if options.save else ""
    if save and not save.lower().endswith(".blend"):
        problems.append(f"--save must end with .blend: {options.save}")
    if save and save == source:
        problems.append("--save points at the source file: write a new file, never over the user's")
    if problems:
        refuse(problems)
    return source, script, save


def main():
    options = parse(sys.argv[1:])
    source, script, save = check(options)
    report(*launch(source, "run_bl.py", [script, save, source], options.timeout))


if __name__ == "__main__":
    guard(main, HINT)
