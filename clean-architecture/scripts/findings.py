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
import findings

findings.RULES = engine.RULES

if __name__ == "__main__":
    guard(findings.main, "edit findings.json in the run folder by hand, one writer at a time")
