import argparse
import importlib.util
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

from common import guard, read_json, write_json
from files import is_data, is_locale, is_test, read_lines, relative, walk
from runs import FINDINGS, MEASURE, load_config, new_run, project_root, runs
from lexer import LANGS, PROSE, PYTHON_SUFFIX, scan

TEXT_SUFFIXES = LANGS.keys() | PROSE | {".json", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".properties", ".po",
                                        ".arb", ".xml", ".gradle", ".env"}
TEXT_NAMES = {"Dockerfile", "Makefile", "Procfile"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp", ".avif", ".svg"}
LISTED = 60


def describe(path, root):
    suffix = path.suffix.lower()
    style, image = LANGS.get(suffix), suffix in IMAGE_SUFFIXES
    lines = [] if image else read_lines(path)
    return {"path": path, "rel": relative(path, root), "lines": lines, "code": bool(style), "image": image,
            "prose": suffix in PROSE, "rows": scan(lines, style, suffix == PYTHON_SUFFIX) if style else [],
            "test": is_test(path, root, lines), "data": is_data(path, root), "locale": is_locale(path, root)}


def wanted(path):
    suffix = path.suffix.lower()
    return (suffix in TEXT_SUFFIXES or suffix in IMAGE_SUFFIXES or path.name in TEXT_NAMES
            or path.name.startswith(".env"))


def load(path):
    spec = importlib.util.spec_from_file_location(f"clean_code_{path.parent.name}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checks(files, root, config):
    findings, stats = [], {}
    for path in sorted((HERE / "checks").glob("*/*.py")):
        found, measured = load(path).check(files, root, config)
        stats.update(measured)
        for finding in found:
            findings.append({"id": f"M{len(findings) + 1}", "status": "candidate", "source": path.stem, **finding})
    return findings, stats


def summary(run, report, findings):
    stats = report["stats"]
    print(f"run: {run}")
    print(f"scope: {report['scope']}, {stats.get('code_files', 0)} code files")
    print(f"previous run: {report['previous'] or 'none'}")
    counts = Counter(finding["rule"] for finding in findings)
    print("candidates by rule: " + (", ".join(f"{rule}: {count}" for rule, count in sorted(counts.items())) or "none"))
    for finding in findings[:LISTED]:
        print(f"{finding['id']} | {finding['rule']} | {finding['file']}:{finding['line']} | {finding['what']} | "
              f"{finding['proof']}")
    if len(findings) > LISTED:
        print(f"{len(findings) - LISTED} more in {run / FINDINGS}")
    for batch, folders in enumerate(stats.get("readers", []), 1):
        print(f"reader {batch}: {', '.join(folders)}")


def main():
    parser = argparse.ArgumentParser(
        description="Measure a scope against the clean-code rules without changing its files.")
    parser.add_argument("scope", nargs="?", default=".")
    parser.add_argument("--boxes", action="append", default=[],
                        help="JSON of chrome-bidi measure_images.py, repeatable")
    parser.add_argument("--out", help="folder for the run, instead of .ia/clean-code at the project root")
    args = parser.parse_args()
    scope = Path(args.scope).resolve()
    if not scope.exists():
        raise FileNotFoundError(f"scope {scope} does not exist")
    root = project_root(scope)
    config = load_config(root)
    config["boxes"] = [box for path in args.boxes for box in read_json(Path(path))]
    files = [describe(path, root) for path in walk(scope, root, config) if wanted(path)]
    findings, stats = run_checks(files, root, config)
    previous = runs(root, args.out)
    run = new_run(root, args.out)
    report = {"scope": relative(scope, root) or ".", "root": str(root), "run": run.name,
              "previous": previous[-1].name if previous else None, "config": config, "stats": stats}
    write_json(run / MEASURE, report)
    payload = {"findings": findings, "unmeasured": [], "checked": []}
    write_json(run / FINDINGS, payload)
    summary(run, report, findings)


if __name__ == "__main__":
    guard(main, "run the per-rule greps listed in SKILL.md and note every count by hand")
