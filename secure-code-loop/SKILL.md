---
name: secure-code-loop
description: Use when the user types /secure-code-loop, when code written or changed must be secured, audited or hardened, when the user asks to run the security scanners, for a security review or for code without flaws, when Semgrep, Gitleaks, Trivy, SonarQube, Bandit, gosec, cargo audit, npm audit or OSV is named, when a secret or a vulnerable dependency turns up, or when the clean-code skill reports security findings.
---

# Secure code loop

Scan, fix, rescan until no serious finding is left in scope. Scanners run on this machine, tests end at least as
green as they started, code does not swell, and no temporary file stays behind. The clean-code skill audits and
tidies; this skill is the loop that gets code through the security scanners.

`<skill>` = this folder. Scripts need Python 3, standard library only, and never install anything:

```
python -I "<skill>/scripts/start.py" --root "<project>" [--base <revision> | --scope <path>...]
python -I "<skill>/scripts/scan.py" --work "<work>" --passed <n> --failed <n>
python -I "<skill>/scripts/finish.py" --work "<work>" [--close --passed <n> --failed <n>]
```

`start.py` records files, uncommitted changes, test digests and line counts in a work folder under system temp
(nothing in the project or `.git`), prints `work:`, three `ledger:` paths, `tool:` lines (ready, missing, not
needed), `stack:` lines (manifests) and `not covered:` for a category without scanner. `scan.py` runs every
scanner present (two workers, below normal priority, JSON into work folder), merges duplicates, raises injection,
path, deserialisation, XXE, SSRF and hardcoded-secret CWEs to high, ends on `stop:` or `continue:`. `finish.py`
deletes what the manifest lists, puts old tests back, prints report material. Exit 2 = `refused:` lines, 1 =
failure. Other flags (`--offline`, `--rules <folder>`, `--timeout`): `--help`.

Scope: `--base` = files changed since that revision; `--scope` = files or folders named; neither = whole project;
files touched after start join it. `--passed`, `--failed` = counts of the test run just before the call, errors
as failed. Row = `<label>: <level> <key> <path>[:<line>] <tools> <ids>: <message>`, key stable across line shifts.

## Rules

These hold on every run, whatever the scope.

1. Never delete, disable, edit or weaken a test that existed at start; one red at start must not get worse.
2. Never silence a finding to make it go away: no `# nosemgrep`, `# nosec`, `// NOSONAR`, `@SuppressWarnings`,
   `gitleaks:allow`, ignore file or rule switched off. Proven false positive = line `<key> <reason>` in
   `false-positives.txt`, reason drawn from real data flow ("internal code" is none); code stays as is.
3. Nothing about the code leaves the machine: no `semgrep login`, no cloud option, no upload. Scanners reach only
   public rule and advisory sources; web queries hold public package names and versions, never code, paths,
   secrets, hosts or project names. `scan.py --offline` cuts all downloads.
4. Fix the cause: swap the dangerous API for the safe one (bound parameters, argument list without shell,
   `yaml.safe_load`, `secrets`), never a filter on top when a safe API exists.
5. Minimal change: touch only what a finding needs, rewrite nothing around it.
6. Scanner missing: install only with user's consent; otherwise go on with what is present, report the gap.
7. Secret found: move it to environment (sample entry in `.env.example`), never print it, tell user to revoke it:
   it sits in git history once committed. Never rewrite history without consent.
8. Only manifest entries get deleted. Each temporary file goes into `manifest.txt` the moment it exists.

Heavy runs: `guard.py wait` of the resource-guard skill before `scan.py` and each test run (Claude Code hook does
it), start on exit 0. Long scan goes through the limited-run skill, so all scanners share one memory cap:

```
python -I "<limited-run>/scripts/run.py" start --name secure-scan -- python -I "<skill>/scripts/scan.py" ...
```

SonarQube is used only when a server already answers on this machine with `SONAR_TOKEN` set; starting one
(docker with `mem_limit` and `--cpus 1`) is the user's call.

## Procedure

Steps 4 to 10 repeat until `scan.py` prints `stop:`.

1. `start.py` with scope. `old temporary:` line = leftover of an earlier run: ask before deleting it.
2. New code to write, or `not covered: code`: read `reference/checklist.md` and review scope files against it.
   Each flaw seen by hand becomes `open <level> review-<n> <file> : <flaw>` in `advisories.txt`, so loop counts it.
3. Baseline: run the project's tests once, note passed and failed.
4. `scan.py` with baseline counts.
5. Known advisories, once after first scan and again after each dependency bump. Machine sources first: `osv`,
   `npm-audit`, `pnpm-audit`, `cargo-audit`, `trivy` rows. Then web search for what they miss: runtime, framework,
   plugin and engine versions behind `stack:` lines, packages without lockfile pin, private registries.
   Query = public name plus version (`<name> <version> CVE`, `<name> <version> security advisory`); trust vendor
   advisory, GitHub Advisory Database or NVD; a forum, blog or unknown repository alone proves nothing (results
   hold fake trackers). Each hit that applies goes into `advisories.txt` as `open <level> <id> <file|-> : <note>`;
   after the fix it turns `fixed`, or `not-applicable` with its reason.
6. Triage in this order: secrets, blocker and critical, high, vulnerable dependency with fix, then medium and
   lower. Each row: read whole function, callers and callees, decide true or false positive.
7. Fix in triage order, per the rules. Dependency: lowest fixed version compatible with the project, through its
   package manager so the lockfile follows, then build. Check the fix opens no new checklist hole (validation
   with ReDoS, lock held during I/O).
8. Non-trivial fix gets a temporary test proving the hostile input is blocked, nothing more: `../../etc/passwd`
   refused, quote in SQL input kept as value, URL to `127.0.0.1` or `169.254.169.254` refused, fresh IV per
   encryption, archive entry with `../` refused. Names: `test_secureloop_tmp_*.py`, `secureloop-tmp-*.test.ts`,
   `*_secureloop_tmp_test.go`, `SecureLoopTmp_*Test.java` or `.php`, `secureloop_tmp_*.spec.luau`. Path into
   `manifest.txt` at once.
9. Run all tests, old and temporary. Old test passing before, failing now: fix is wrong or too broad, redo it.
   Temporary test failing: fix incomplete.
10. `scan.py` with new counts; act on its last line (table below).
11. On `stop:`: each temporary test passing now stays as regression test: rename it to project's test naming
    without the `secureloop_tmp` part (`test_secureloop_tmp_sql.py` -> `test_security_sql.py`), drop its line
    from `manifest.txt`. Failing one stays listed and gets deleted. Then `finish.py`, then old tests once more,
    then `finish.py --close` with those counts.
12. Report (last section).

## Lines of scan.py

Last line decides; others say what to do before the next scan.

| Line | Do |
|---|---|
| `stop: clean` | no blocking finding in scope, tests at least as green as iteration 1: step 11 |
| `stop: limit of 5 iterations` | step 11, report what remains |
| `stop: stalled, ...` | blocking count did not drop over two iterations: step 11, present remaining rows to user as design decisions |
| `stop: no scanner ran` | step 2 by hand, then step 11; ask user before installing a scanner |
| `continue: <n> blocking in scope` | fix `fix:` rows, step 9, rescan |
| `continue: ..., tests worse than iteration 1` | regression first: redo the fix, never the old test |
| `continue: ..., old tests touched` | rule 1 broken: undo the change to old tests, rescan |
| `fix:` | blocking in scope: fix |
| `also:` | medium or lower in scope: fix when cheap, else report |
| `elsewhere:` | blocking outside scope: report, fix only with user's consent |
| `revoke:` | secret in git history: rule 7, never blocks |
| `more: <n> rows in findings.json` | rest in `<work>/iteration-<n>/findings.json` |
| `tool: <name> <place> missing` | rule 6 |
| `tool: <name> <place> failed: ...` | rerun once; failing again, report it |
| `tool: <name> <place> skipped: ...` | offline, no server or nothing to scan: report it |
| `not covered: code`, `secrets`, `dependencies` | code: step 2; secrets: `rg` line of the checklist; dependencies: step 5 by web |
| `bad line: <ledger>: ...` | that ledger line is not applied: fix it |
| `bloat: over 30%, ...` | share one helper instead of copies, drop extra checks |
| `changed test:`, `missing test:` | rule 1 broken: undo now |

## Lines of finish.py

Cleanup lines come first, report material after.

| Line | Do |
|---|---|
| `deleted: <file>` | nothing |
| `kept: <entry> (a folder: list its files)` | put its files in the manifest, rerun `finish.py` |
| `kept: <entry> (<why>)` | existed at start, ignored, tool folder or outside project: never delete it by hand |
| `restored: <file>` | old test or file put back from git: rerun old tests |
| `changed test:`, `missing test:`, `gone:` | could not be put back (uncommitted at start, no git): tell user |
| `left: <file>` | temporary file missing from manifest: add it, rerun `finish.py` |
| `new since start: <file>` | kept; name it in report so user sees it |
| `tool: <name> <place> skipped: ...` or `failed: ...` | that place went unchecked at the last scan: report it as not covered |
| `closed: <work> deleted` | done |

`--close` refuses while `changed test:`, `missing test:` or `left:` lines remain, or tests are worse than iteration 1.

## Report

Short, in the user's language, from `finish.py` lines:

- tools used, tools missing, what was not covered;
- blocking findings at iteration 1 and at last scan, by level;
- each fix on one line: file, problem, fix;
- false positives with reason, advisories with state;
- what remains and why (out of scope, design decision, iteration limit);
- secrets to revoke;
- tests at start and at end;
- cleanup: security tests kept as regression tests, other temporary files deleted, no old test touched.

No step-by-step story, no copy of JSON.
