import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

import engine

if engine.MISSING:
    print(f"clean-architecture: {engine.MISSING}")
    print("by hand: install the clean-code skill next to this one")
    sys.exit(engine.FAILED)

from common import guard
import plan_check

plan_check.PHASES = engine.PHASES
plan_check.MARKER = engine.MARKER

if __name__ == "__main__":
    guard(plan_check.main, "tick every confirmed id against the plan by hand and check the phase order")
