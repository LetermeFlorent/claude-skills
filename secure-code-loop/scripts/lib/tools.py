import shutil
from collections import namedtuple
from pathlib import PurePosixPath

import osv
import parsers
import sonar
from common import ENCODING, read_json, run, write_json
from parsers import OK, verdict
from project import SKIPPED_DIRS, is_code

DEFAULT_TIMEOUT = 900
WORKERS = 2
RUNS = "runs.json"
MISSING = "missing"
CODE, SECRETS, DEPENDENCIES = "code", "secrets", "dependencies"
SEMGREP_PACKS = ("p/default", "p/owasp-top-ten", "p/secrets")
BANDIT_EXCLUDES = ",".join(f"*/{name}/*" for name in sorted(SKIPPED_DIRS))
MANIFESTS = frozenset("package.json package-lock.json pnpm-lock.yaml yarn.lock pyproject.toml poetry.lock uv.lock "
                      "Pipfile.lock Cargo.toml Cargo.lock composer.json composer.lock go.mod go.sum Gemfile.lock "
                      "pom.xml build.gradle build.gradle.kts wally.toml wally.lock".split())
Tool = namedtuple("Tool", "name program covers places runner parser")
Context = namedtuple("Context", "root names is_git offline rules timeout")


def base(name):
    return PurePosixPath(name).name


def is_manifest(name):
    return base(name) in MANIFESTS or bool(osv.REQUIREMENTS.match(base(name)))


def at_root(names, is_git):
    return ["."]


def in_git(names, is_git):
    return ["."] if is_git else []


def with_suffix(suffix):
    return lambda names, is_git: ["."] if any(name.endswith(suffix) for name in names) else []


def beside(lockfile):
    return lambda names, is_git: sorted({PurePosixPath(name).parent.as_posix() for name in names
                                         if base(name) == lockfile})


def with_lockfiles(names, is_git):
    return ["."] if any(base(name) in osv.READERS or osv.REQUIREMENTS.match(base(name)) for name in names) else []


def external(argv_of, stdout=False):
    def runner(context, place, output):
        argv = argv_of(output, context)
        if isinstance(argv, str):
            return argv
        code, out, err = run(argv, context.root / place, context.timeout)
        if code is None:
            return f"failed: {err}"
        if stdout:
            output.write_text(out, encoding=ENCODING)
        return verdict(read_json(output), code, err or out)
    return runner


def online(*argv):
    return lambda output, context: "skipped: offline" if context.offline else list(argv)


def semgrep_argv(output, context):
    if context.offline and not context.rules:
        return "skipped: offline and no --rules folder"
    configs = [str(context.rules)] if context.rules else SEMGREP_PACKS
    return ["semgrep", "scan", "--metrics=off", "--disable-version-check", "--quiet", "--json", f"--output={output}",
            f"--jobs={WORKERS}", *(f"--config={config}" for config in configs), "."]


def gitleaks_argv(kind):
    return lambda output, context: ["gitleaks", kind, ".", "--report-format=json", f"--report-path={output}",
                                    "--redact", "--no-banner", "--exit-code=0", "--log-level=error"]


def trivy_argv(output, context):
    offline = ["--skip-db-update", "--offline-scan"] if context.offline else []
    return ["trivy", "fs", "--scanners=vuln,secret,misconfig", "--format=json", f"--output={output}", "--quiet",
            f"--parallel={WORKERS}", *offline, "."]


def osv_runner(context, place, output):
    if context.offline:
        return "skipped: offline"
    try:
        osv.scan(context.root, context.names, output)
    except (OSError, ValueError) as error:
        return f"failed: {error}"
    packages = (read_json(output) or {}).get("packages", 0)
    return f"{OK}, {packages} packages" if packages else "skipped: no pinned public package"


TOOLS = (
    Tool("semgrep", "semgrep", (CODE, SECRETS), at_root, external(semgrep_argv), parsers.semgrep),
    Tool("gitleaks", "gitleaks", (SECRETS,), at_root, external(gitleaks_argv("dir")), parsers.gitleaks),
    Tool("gitleaks-history", "gitleaks", (), in_git, external(gitleaks_argv("git")), parsers.gitleaks),
    Tool("trivy", "trivy", (DEPENDENCIES, SECRETS), at_root, external(trivy_argv), parsers.trivy),
    Tool("bandit", "bandit", (CODE,), with_suffix(".py"),
         external(lambda output, context: ["bandit", "-r", ".", "-f", "json", "-o", str(output), "-q",
                                           "-x", BANDIT_EXCLUDES]), parsers.bandit),
    Tool("gosec", "gosec", (CODE,), beside("go.mod"),
         external(lambda output, context: ["gosec", "-fmt=json", f"-out={output}", "-no-fail", "./..."]),
         parsers.gosec),
    Tool("cargo-audit", "cargo-audit", (DEPENDENCIES,), beside("Cargo.lock"),
         external(lambda output, context: ["cargo", "audit", "--json",
                                           *(["--no-fetch", "--no-yanked"] if context.offline else [])], True),
         parsers.cargo_audit),
    Tool("npm-audit", "npm", (DEPENDENCIES,), beside("package-lock.json"),
         external(online("npm", "audit", "--json"), True), parsers.npm_audit),
    Tool("pnpm-audit", "pnpm", (DEPENDENCIES,), beside("pnpm-lock.yaml"),
         external(online("pnpm", "audit", "--json"), True), parsers.pnpm_audit),
    Tool("osv", None, (DEPENDENCIES,), with_lockfiles, osv_runner, osv.parse),
    Tool("sonar", "sonar-scanner", (CODE,), at_root,
         lambda context, place, output: sonar.analyse(context.root, output, context.timeout) or OK, sonar.parse),
)
BY_NAME = {tool.name: tool for tool in TOOLS}


def installed(tool):
    return not tool.program or bool(shutil.which(tool.program))


def run_all(context, folder):
    runs = []
    for tool in TOOLS:
        for index, place in enumerate(tool.places(context.names, context.is_git)):
            output = folder / f"{tool.name}-{index}.json"
            state = tool.runner(context, place, output) if installed(tool) else MISSING
            runs.append({"tool": tool.name, "place": place, "file": output.name, "state": state})
    write_json(folder / RUNS, runs)
    return runs


def not_covered(runs, names):
    needed = {SECRETS} | ({CODE} if any(is_code(name) for name in names) else set()) | (
        {DEPENDENCIES} if any(is_manifest(name) for name in names) else set())
    done = {category for entry in runs if entry["state"].startswith(OK)
            for category in BY_NAME[entry["tool"]].covers}
    return sorted(needed - done)
