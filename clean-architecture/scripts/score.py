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
import score

score.EACH = engine.EACH
score.SHARE = {}
score.LONG_FILES = None
score.READ_RULES = engine.READ_RULES

if __name__ == "__main__":
    guard(score.main, "start from 20, take off the points of SKILL.md for each confirmed finding")
