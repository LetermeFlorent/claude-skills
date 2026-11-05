import os
import shutil
import stat
import sys

from gitcalls import GitFailed, git, latest_release


def installed_tag(folder):
    try:
        return git(folder, "describe", "--tags", "--exact-match", "HEAD")
    except GitFailed:
        return ""


def update_checkout(folder, url):
    if folder.exists() and not (folder / ".git").is_dir():
        return False, f"{folder} is not ours, left as is"
    if not folder.exists():
        folder.mkdir(parents=True)
        git(folder, "init", "--quiet")
        git(folder, "remote", "add", "origin", url)
    latest = latest_release(folder)
    if latest is None:
        return False, "no release found"
    tag, was = latest[0], installed_tag(folder)
    if was == tag:
        return True, f"up to date ({tag})"
    git(folder, "fetch", "--quiet", "--depth", "1", "--no-tags", "origin", f"refs/tags/{tag}:refs/tags/{tag}")
    git(folder, "checkout", "--quiet", "--force", "--detach", f"{tag}^{{commit}}")
    return True, f"updated {was} to {tag}" if was else f"installed {tag}"


def _force(function, path, _):
    os.chmod(path, stat.S_IWRITE)
    function(path)


def remove_checkout(folder):
    if not (folder / ".git").is_dir():
        return False
    handler = {"onexc": _force} if sys.version_info >= (3, 12) else {"onerror": _force}
    shutil.rmtree(folder, **handler)
    return True
