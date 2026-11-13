import sys
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1]
CLEAN_CODE = SCRIPTS.parents[1] / "clean-code" / "scripts"
LIB = "lib"
sys.path[:0] = [str(SCRIPTS / LIB), str(CLEAN_CODE / LIB), str(CLEAN_CODE), str(CLEAN_CODE / "checks" / "project")]

RULES = range(11)
READ_RULES = (9, 10)
EACH = {1: (1, 3), 2: (0.5, 2), 3: (0.5, 2), 4: (0.5, 2), 5: (1, 3), 6: (0.25, 1), 7: (0.25, 1), 8: (0.5, 1),
        9: (0.5, 2), 10: (0.5, 2)}
PHASES = {0: 1, 3: 1, 1: 2, 2: 3, 4: 3, 6: 3, 8: 3, 7: 4, 5: 5, 9: 5, 10: 5}
FAILED = 1
MARKER = "<!-- clean-architecture plan v1 -->"
DEFAULTS = {"max_depth": 6, "group_min": 3}
MISSING = None if (CLEAN_CODE / "measure.py").is_file() else f"clean-code skill not found at {CLEAN_CODE.parent}"

if not MISSING:
    import runs

    runs.TOOL_PARTS = (".ia", "clean-architecture")
    runs.DEFAULTS.update(DEFAULTS)
