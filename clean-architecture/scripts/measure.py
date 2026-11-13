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
import measure

measure.HERE = engine.SCRIPTS

if __name__ == "__main__":
    guard(measure.main, "no run folder was written: report this error and stop the audit")
