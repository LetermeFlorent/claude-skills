import sys

sys.dont_write_bytecode = True
import argparse
import filecmp
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from common import ENCODING, guard, refuse
from gitrepo import ensure_exclude, toplevel, tracked_under
from images import probe, size_text
from index import FOLDER, INDEX, entries, problems, with_lines

HINT = "copy the images into <project>/.ia/references/ and write one line per image in references.md"


def sources(paths):
    found, skipped, missing = [], [], []
    for raw in paths:
        path = Path(raw).resolve()
        if path.is_dir():
            for child in sorted(p for p in path.iterdir() if p.is_file()):
                (found if probe(child)[0] else skipped).append(child)
        elif path.is_file():
            (found if probe(path)[0] else missing).append(path)
        else:
            missing.append(path)
    return found, skipped, missing


def target(folder, source):
    candidate = folder / source.name
    number = 2
    while candidate.exists() and not filecmp.cmp(candidate, source, shallow=False):
        candidate = folder / f"{source.stem}-{number}{source.suffix}"
        number += 1
    return candidate


def git_problems(project):
    root = toplevel(project) if project.is_dir() else None
    if root is None:
        print("git: no repository yet; check again once git init has run, it excludes .ia/")
        return []
    if ensure_exclude(root):
        print(f"git: added .ia/ to the exclude file of {root.as_posix()}")
    return [f"{path} is tracked by git: references are never committed" for path in tracked_under(root)]


def show(folder):
    text = (folder / INDEX).read_text(encoding=ENCODING) if (folder / INDEX).exists() else ""
    known = entries(text)
    files = {p.name: probe(p) for p in sorted(folder.iterdir()) if p.is_file() and p.name != INDEX}
    for name, (form, size) in files.items():
        print(f"{(folder / name).as_posix()} | {form or 'not an image'} | {size_text(size)} | "
              f"{known.get(name, 'no line')}")
    return text, {name: form for name, (form, _) in files.items()}


def add(project, paths):
    found, skipped, missing = sources(paths)
    if missing or not found:
        refuse([f"{p.as_posix()} is not an image file or folder" for p in missing] or ["no image found"])
    folder = project.joinpath(*FOLDER)
    folder.mkdir(parents=True, exist_ok=True)
    names = []
    for source in found:
        copy = target(folder, source)
        if not copy.exists():
            shutil.copy2(source, copy)
        names.append(copy.name)
    index = folder / INDEX
    text = index.read_text(encoding=ENCODING) if index.exists() else ""
    index.write_text(with_lines(text, names), encoding=ENCODING, newline="\n")
    for path in skipped:
        print(f"skipped, not an image: {path.as_posix()}")
    git_problems(project)
    show(folder)
    print(f"next: open each image, then replace each '(à décrire)' in {index.as_posix()}")


def check(project):
    folder = project.joinpath(*FOLDER)
    if not (folder / INDEX).exists():
        refuse([f"no {INDEX} in {folder.as_posix()}: run add first"])
    text, files = show(folder)
    found = problems(text, files) + git_problems(project)
    if found:
        refuse(found)
    print(f"references ok: {len(files)} image(s)")


def main():
    parser = argparse.ArgumentParser(prog="references.py", description="Keep a project's reference images.")
    commands = parser.add_subparsers(dest="command", required=True)
    adding = commands.add_parser("add", help="copy images or folders of images into <project>/.ia/references")
    adding.add_argument("project")
    adding.add_argument("paths", nargs="+")
    checking = commands.add_parser("check", help="list the references and refuse what is missing")
    checking.add_argument("project")
    args = parser.parse_args()
    project = Path(args.project).resolve()
    if args.command == "add":
        add(project, args.paths)
    else:
        check(project)


if __name__ == "__main__":
    guard(main, HINT)
