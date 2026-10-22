import os
import shutil
import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from common import FAILED, REFUSED, guard, joined, refuse, run
from message import ATTRIBUTION
from repo import (GIT, GITHUB_KIND, NO_REMOTE, ORIGIN, OTHER_KIND, branch, find_root, message, operation, remote,
                  unpushed)

PUSH_TIMEOUT = 180
ACCOUNTS_VAR = "CLAUDE_SKILLS_ACCOUNTS"
SHELL = "sh"
SERVICE = "github"
ACCOUNTS_RUN = "run"
TOKEN_HELPER = "credential.helper=!f() { echo username=x-access-token; echo password=$GH_TOKEN; }; f"
REJECTED = ("rejected", "non-fast-forward", "fetch first")


def _push_args(name, upstream):
    return ["push"] if upstream else ["push", "-u", ORIGIN, name]


def _accounts_tool():
    value = os.environ.get(ACCOUNTS_VAR)
    return Path(value) if value else None


def _command(root, target, args, accounts=None):
    accounts = accounts or _accounts_tool()
    git = [GIT, "-c", "credential.helper=", "-c", TOKEN_HELPER, *args]
    if target["kind"] == GITHUB_KIND and accounts and accounts.exists():
        return [shutil.which(SHELL) or SHELL, str(accounts), ACCOUNTS_RUN, SERVICE, target["owner"], "--cwd",
                root.as_posix(), "--", *git]
    return [GIT, *args]


def _problems(root, name, target):
    busy = operation(root)
    problems = [] if name else ["detached HEAD: ask the user which branch to push"]
    problems += [f"a {busy} is in progress"] if busy else []
    if target["kind"] == OTHER_KIND:
        problems.append(f"{target['url']} is neither GitHub nor a local or ssh remote: push it by hand")
    marked = [commit for commit in unpushed(root) if ATTRIBUTION.search(message(root, commit))]
    problems += [f"{len(marked)} unpushed commits carry an attribution: run scrub.py first"] if marked else []
    return problems


def main():
    root = find_root(Path.cwd())
    name, upstream = branch(root)
    target = remote(root)
    if target["kind"] == NO_REMOTE:
        print("no remote: the commits stay local")
        return
    problems = _problems(root, name, target)
    if problems:
        refuse(problems)
    if not unpushed(root) and upstream:
        print("nothing to push")
        return
    code, out, err = run(_command(root, target, _push_args(name, upstream)), root, PUSH_TIMEOUT)
    output = joined(out, err)
    if code == 0:
        print(f"pushed {name} to {target['url']}")
    elif any(word in output for word in REJECTED):
        print(f"rejected, the remote has commits this branch lacks. Never forced: the user runs git pull --rebase\n"
              f"{output}")
        sys.exit(REFUSED)
    else:
        print(f"push failed, not retried:\n{output}")
        sys.exit(FAILED)


if __name__ == "__main__":
    guard(main, "push through the account-keys skill when it is installed, else with the user's own credentials")
