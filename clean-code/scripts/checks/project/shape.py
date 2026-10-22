import fnmatch
import os
from collections import Counter
from pathlib import PurePosixPath

SIZE_RULE = 1
FOLDER_RULE = 4
TOOLING_RULE = 12
TEST_RULE = 9
LINT_PATTERNS = (".eslintrc*", "eslint.config.*", "biome.json*", ".prettierrc*", "prettier.config.*", "ruff.toml",
                 ".ruff.toml", ".flake8", ".pylintrc", ".golangci.*", ".rubocop.yml", "*rustfmt.toml", "clippy.toml",
                 "checkstyle*.xml", ".swiftlint.yml", "detekt*.yml", ".clang-format", ".clang-tidy", "deno.json*",
                 ".stylelintrc*", ".editorconfig")
LINT_MARKERS = ("eslint", "prettier", "@biomejs", "[tool.ruff", "[tool.black", "[tool.pylint", "[tool.flake8",
                "spotless", "ktlint", "checkstyle", "detekt")
MANIFESTS = {"package.json", "pyproject.toml", "setup.cfg", "Cargo.toml", "go.mod", "build.gradle", "build.gradle.kts",
             "pom.xml", "Gemfile", "composer.json", "deno.json"}
BUILT_IN = {"Cargo.toml", "go.mod", "deno.json"}
DEEPEST = 3


def _tooled(root, folder, files):
    names = os.listdir(root / folder) if (root / folder).is_dir() else []
    if any(fnmatch.fnmatch(name, pattern) for name in names for pattern in LINT_PATTERNS):
        return True
    if BUILT_IN & set(names):
        return True
    manifests = [item for item in files if PurePosixPath(item["rel"]).parent == folder and
                 PurePosixPath(item["rel"]).name in MANIFESTS]
    return any(marker in "\n".join(item["lines"]) for item in manifests for marker in LINT_MARKERS)


def _batches(code, scope_depth, readers):
    groups = Counter()
    for depth in range(1, DEEPEST + 1):
        groups = Counter("/".join(PurePosixPath(item["rel"]).parts[:scope_depth + depth][:-1] or ["."]) or "."
                         for item in code)
        if len(groups) >= readers:
            break
    loads = [[0, []] for _ in range(readers)]
    for folder, count in groups.most_common():
        lightest = min(loads, key=lambda load: load[0])
        lightest[0] += count
        lightest[1].append(folder)
    return [sorted(folders) for _, folders in loads if folders]


def check(files, root, config):
    code = [item for item in files if item["code"] and not item["data"] and not item["locale"]]
    findings = []
    for item in code:
        if len(item["lines"]) > config["max_lines"]:
            findings.append({"rule": SIZE_RULE, "file": item["rel"], "line": 1,
                             "what": f"{len(item['lines'])} lines > {config['max_lines']}", "proof": "line count"})
    folders = Counter(str(PurePosixPath(item["rel"]).parent) for item in code)
    for folder, count in sorted(folders.items()):
        if count > config["max_files"]:
            findings.append({"rule": FOLDER_RULE, "file": folder, "line": 0,
                             "what": f"{count} code files > {config['max_files']}", "proof": "files in folder"})
    projects = {PurePosixPath(item["rel"]).parent for item in files if PurePosixPath(item["rel"]).name in MANIFESTS}
    for folder in sorted(projects or {PurePosixPath(".")}):
        if code and not _tooled(root, folder, files):
            findings.append({"rule": TOOLING_RULE, "file": str(folder), "line": 0,
                             "what": "no lint or formatter configured",
                             "proof": "no lint config file, no lint entry in the manifest"})
    tests = sum(item["test"] for item in code)
    if code and not tests:
        findings.append({"rule": TEST_RULE, "file": ".", "line": 0, "what": "no test file at all",
                         "proof": "0 test files"})
    readers = config["readers"]
    scope_depth = min(len(PurePosixPath(item["rel"]).parts) for item in code) - 1 if code else 0
    stats = {"code_files": len(code), "test_files": tests, "over_lines": sum(f["rule"] == 1 for f in findings),
             "languages": dict(Counter(item["path"].suffix.lower() for item in code).most_common()),
             "readers": _batches(code, scope_depth, readers) if len(code) > config["reader_threshold"] else []}
    return findings, stats
