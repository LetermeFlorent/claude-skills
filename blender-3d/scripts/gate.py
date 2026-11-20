import argparse
import json
import sys
sys.dont_write_bytecode = True
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from blender import FAILED, REFUSED, existing, guard, launch, refuse, useful
from gate_rules import parse_measure, parse_rows, verdicts

HINT = "check each minimum of model-design section 3 on the captures by hand"


def options():
    parser = argparse.ArgumentParser(description="Refuse a creature that misses a minimum of model-design.")
    parser.add_argument("source", help="exported .glb or .blend of the creature")
    parser.add_argument("--body", required=True, help="name of the skinned body mesh")
    parser.add_argument("--wings", nargs="*", default=[], help="membrane meshes; each loose piece is one wing")
    parser.add_argument("--plates", nargs="*", default=[], help="NAME:COUNT of each plate mesh, from the sheet")
    parser.add_argument("--spikes", nargs="*", default=[], help="NAME:COUNT of each spike or tooth row mesh")
    parser.add_argument("--horns", nargs="*", default=[], help="horn meshes; each loose piece is one horn")
    parser.add_argument("--show", action="store_true", help="print every measure, kept ones included")
    parser.add_argument("--timeout", type=int, default=600)
    return parser.parse_args()


def main():
    given = options()
    problems = []
    source = existing(given.source, problems, "source")
    plates, error = parse_rows(given.plates)
    spikes, error2 = parse_rows(given.spikes)
    problems += [e for e in (error, error2) if e]
    if problems or source == "-":
        refuse(problems or ["give the exported creature"])
    plan = {"body": given.body, "wings": given.wings, "plates": list(plates), "spikes": list(spikes),
            "horns": given.horns}
    code, output = launch(source, "gate_bl.py", [source, json.dumps(plan)], given.timeout)
    lines = useful(output) if code is not None else [f"failed: {output}"]
    measures = [m for m in map(parse_measure, lines) if m]
    for line in lines:
        if given.show or not line.startswith("measure "):
            print(line)
    if code != 0 or not measures:
        print(f"failed: Blender exit code {code}")
        sys.exit(FAILED)
    refused, kept = verdicts(measures, {**plates, **spikes})
    for line in refused:
        print(f"refused: {line}")
    print(f"gate: {kept} kept, {len(refused)} refused")
    if refused:
        print("not deliverable: fix each refused line at its pass, export again, run gate.py again")
        sys.exit(REFUSED)
    print("deliverable: every measured minimum kept; the captures still decide the rest")


if __name__ == "__main__":
    guard(main, HINT)
