import argparse
import sys

sys.dont_write_bytecode = True
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from plan import load_plan
from rules import check_plan

TOOL = "dispatching-parallel-agents"
REFUSED, FAILED = 2, 1


def main():
    parser = argparse.ArgumentParser(description="Check that a dispatch plan holds independent agents.")
    parser.add_argument("plan", help="JSON file: a list of agents with name, writes, tree, ports, instances, flags")
    args = parser.parse_args()
    agents = load_plan(Path(args.plan).read_text(encoding="utf-8"))
    problems = check_plan(agents)
    if problems:
        print("not independent, do not dispatch as planned:")
        for problem in problems:
            print(f"  {problem}")
        sys.exit(REFUSED)
    print(f"independent: {len(agents)} agents can run together")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        print(f"{TOOL}: {type(error).__name__}: {error}")
        print('by hand: compare the agents\' files, ports and MCP instances in the plan')
        sys.exit(FAILED)
