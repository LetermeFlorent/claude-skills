import sys

sys.dont_write_bytecode = True
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from graphify import install_now
from guard import run_guarded
from paths import GRAPHIFY_FILE, repo_dir, state_file

HINT = "by hand: pip install --user --upgrade graphifyy, then run tools/install.py"


def main(argv):
    repo = repo_dir()
    state = state_file(repo, GRAPHIFY_FILE)
    try:
        ok, text = install_now(repo.parent, state, argv[0])
    finally:
        state.with_suffix(".lock").unlink(missing_ok=True)
    print(text, flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(run_guarded(lambda: main(sys.argv[1:]), HINT))
