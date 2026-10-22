import re
import sys

sys.dont_write_bytecode = True
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

import repo
import verdict
from common import guard, refuse

GITHUB = re.compile(r"github\.com[:/](?P<owner>[^/]+)/")
IA = ".ia"


def _base(root, name):
    counts = {other: repo.ahead(root, other) for other in repo.local_branches(root) if other != name}
    return verdict.pick_base({key: value for key, value in counts.items() if value is not None})


def _stop_reasons(root, name, base, kind):
    busy = repo.operation(root)
    reasons = [f"a {busy} is in progress: finish or abort it first"] if busy else []
    if name in verdict.BASE_NAMES:
        reasons.append(f"{name} is a base branch: go to the feature branch or its worktree first")
    elif not base and kind != verdict.KINDS[2]:
        reasons.append(f"{name or 'HEAD'} has no other local branch to merge into: nothing to finish")
    elif base and kind != verdict.KINDS[2] and not repo.ahead(root, base):
        reasons.append(f"{name} holds no commit that {base} lacks: nothing to finish")
    return reasons


def _where(root):
    git_dir, common = repo.directories(root)
    main_root = common.parent
    return git_dir, common, main_root


def _land(root, base):
    merged = bool(base) and repo.is_ancestor(root, "HEAD", base)
    return merged, repo.on_remote(root)


def _print_work(root, base):
    log = repo.commits(root, base)
    print(f"commits: {len(log)} ahead of {base}")
    for line in log:
        print(f"  {line}")
    marked = [sha for sha, body in repo.bodies(root, base) if verdict.has_attribution(body)]
    print(f"attribution: {', '.join(marked) if marked else 'none'}")


def _print_cleanup(root, kind, main_root, landing):
    merged, remotes = landing
    dirty = repo.dirty(root)
    ia_files = repo.folder_files(root / IA) if root != main_root else 0
    owned = kind == verdict.KINDS[1] and verdict.owned_worktree(root.as_posix(), main_root.as_posix())
    ok, why = verdict.removal(owned, merged or bool(remotes), len(dirty), ia_files)
    print(f"merged into base: {'yes' if merged else 'no'}")
    print(f"pushed: {', '.join(remotes) if remotes else 'no'}")
    print(f"uncommitted: {len(dirty)}")
    for line in dirty:
        print(f"  {line}")
    print(f"worktree .ia files: {ia_files}")
    print(f"worktree removable now: {'yes' if ok else 'no'} ({why})")


def _print_project(root, main_root):
    names = repo.tracked_names(root)
    url = repo.remote_url(root)
    owner = GITHUB.search(url)
    print(f"remote: {url or 'none'}" + (f" (github account {owner.group('owner')})" if owner else ""))
    hints = verdict.test_hints({Path(name).name for name in names})
    print(f"test hints: {', '.join(hints) if hints else 'none found: read CLAUDE.md, CONTRIBUTING, README'}")
    print(f"pull request template: {verdict.find_template(names) or 'none'}")
    print(f"main repository: {main_root.as_posix()}")


def main():
    root = repo.find_root(Path.cwd())
    git_dir, common, main_root = _where(root)
    name = repo.branch_name(root)
    kind = verdict.environment(git_dir, common, name)
    base, unsure = _base(root, name)
    reasons = _stop_reasons(root, name, base, kind)
    if reasons:
        refuse(reasons)
    print(f"branch: {name or 'detached HEAD'}  environment: {kind}  worktree: {root.as_posix()}")
    print(f"upstream: {repo.upstream(root) or 'none'}")
    print(f"base: {base}" + (" (ambiguous: ask which)" if unsure else ""))
    if base:
        _print_work(root, base)
    _print_cleanup(root, kind, main_root, _land(root, base))
    _print_project(root, main_root)


if __name__ == "__main__":
    guard(main, "git status; git log --oneline; git worktree list")
