import re
from collections import Counter, defaultdict
from pathlib import PurePosixPath

from files import SKIP_DIRS

USELESS_RULE = 3
CROWDED_RULE = 4
DEPTH_RULE = 6
WORD = re.compile(r"[_\-.]|(?<=[a-z0-9])(?=[A-Z])")
CHAIN_MIN = 2
SURELY_FILLED = 64


def entries(path):
    try:
        listed = list(path.iterdir())
    except OSError:
        return [], []
    dirs = [entry for entry in listed if entry.is_dir() and entry.name not in SKIP_DIRS
            and not entry.name.startswith(".")]
    full = [entry for entry in listed if entry.is_file() and _filled(entry)]
    return dirs, full


def _filled(path):
    try:
        return path.stat().st_size > SURELY_FILLED or bool(path.read_bytes().strip())
    except OSError:
        return True


def prefix_groups(stems, least):
    counts = Counter(WORD.split(stem)[0].lower() for stem in stems)
    return {word: count for word, count in counts.items() if count >= least and count < len(stems)}


def crowded(files, config):
    code = defaultdict(list)
    for item in files:
        if item["code"] and not item["test"] and not item["data"] and any(line.strip() for line in item["lines"]):
            code[str(PurePosixPath(item["rel"]).parent)].append(PurePosixPath(item["rel"]).stem)
    findings = []
    for folder, stems in sorted(code.items()):
        if len(stems) > config["max_files"]:
            groups = prefix_groups(stems, config["group_min"])
            split = ", ".join(f"{word}/ ({count})" for word, count in sorted(groups.items()))
            hint = f"group into {split}" if split else "no name prefix to split by, group by reading"
            findings.append({"rule": CROWDED_RULE, "file": folder, "line": 0,
                             "what": f"{len(stems)} code files > {config['max_files']}, {hint}",
                             "proof": "files in folder, prefixes of their names"})
    return findings


def shape(files, root, config):
    folders = {str(parent) for item in files for parent in PurePosixPath(item["rel"]).parents if str(parent) != "."}
    passing = {}
    findings = []
    for folder in sorted(folders):
        dirs, full = entries(root / folder)
        passing[folder] = len(dirs) == 1 and not full
        if not dirs and not full:
            findings.append({"rule": USELESS_RULE, "file": folder, "line": 0, "what": "folder holds only empty files",
                             "proof": "no subfolder, every file empty"})
        if len(PurePosixPath(folder).parts) > config["max_depth"]:
            findings.append({"rule": DEPTH_RULE, "file": folder, "line": 0,
                             "what": f"{len(PurePosixPath(folder).parts)} levels > {config['max_depth']}",
                             "proof": "path depth from the project root"})
    for folder in sorted(passing):
        if not passing[folder] or passing.get(str(PurePosixPath(folder).parent)):
            continue
        chain = [folder]
        while passing.get(chain[-1]):
            dirs, _ = entries(root / chain[-1])
            chain.append(f"{chain[-1]}/{dirs[0].name}")
        if len(chain) - 1 >= CHAIN_MIN:
            findings.append({"rule": DEPTH_RULE, "file": folder, "line": 0,
                             "what": f"{len(chain) - 1} folders in a row hold one subfolder and nothing else",
                             "proof": " > ".join(chain)})
    return findings


def check(files, root, config):
    code = sum(item["code"] and not item["data"] for item in files)
    return crowded(files, config) + shape(files, root, config), {"code_files": code}
