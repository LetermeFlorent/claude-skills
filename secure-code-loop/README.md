# secure-code-loop

To install it, see `INSTALL.md` at the root of the repository.

When code has to be secured, the agent runs the security scanners it finds on your PC, fixes what they report, and scans again until nothing serious is left in the part of the code you care about. It never weakens a test you already had. It never hides a finding to make it go away, and it deletes only the temporary files it created itself.

## What happens

First the agent takes a snapshot of the project: which files exist, which ones hold changes you have not committed, what every existing test looks like. The snapshot goes to a work folder in the system temporary folder, never inside your project or its `.git` folder.

It runs your tests once to know where they stand, then every scanner it finds. Their results are merged into one list, sorted by severity and split between the files of the task and the rest of the project. The agent fixes the serious ones, writes small temporary tests proving each fix blocks a hostile input, runs all the tests and scans again. It stops when nothing serious is left and the tests are at least as green as at the start. It also stops after 5 rounds, or when two rounds in a row bring no progress: what is left then usually needs a design decision, and you get the list.

Scanners do not know every flaw. So the agent also looks up known vulnerabilities of the libraries and versions your project uses, first in public advisory databases, then with web searches that hold only public package names and versions. When no code scanner is installed, it reads the code itself against the checklist in `reference/checklist.md`.

A password or key found in the code is moved to an environment variable, and you are told to revoke it: it stays in the git history. The agent never rewrites that history without asking.

At the end the security tests it wrote and that pass stay in your project, renamed like your other tests, so the flaw cannot come back unnoticed. It deletes the other temporary files it listed, and puts back from git any existing test or file that was changed or removed. Files you had not committed are never put back or reset; you are told about them instead. You get a short report in your language: tools used and missing, what was fixed, false positives with their reason, what is left and why, secrets to revoke, tests before and after.

## Scanners and the network

The skill uses what is installed and never installs anything; a missing scanner is named in the report. Here is what each one reaches. None of them gets your code, except SonarQube, and only when the server runs on this PC.

| Tool | What it reaches | What it sends |
|---|---|---|
| Semgrep | the Semgrep registry, to download its rule packs | nothing about your code, usage metrics off |
| Gitleaks | nothing | nothing |
| Trivy | public registries, to download its vulnerability databases | nothing about your code |
| Bandit | nothing | nothing |
| gosec | nothing itself; the Go tools it calls may download missing modules | module names and versions |
| cargo audit | GitHub, to update the RustSec advisory database, and crates.io to spot withdrawn versions | crate names |
| npm audit, pnpm audit | the npm registry | names and versions of your dependencies |
| OSV | `api.osv.dev` | names and versions of the packages pinned from public registries |
| SonarQube | your own server, only at `localhost` | your code, to that server |
| Web search | a search engine | public package names and versions |

An offline run stops every download and every query. Semgrep then needs a local rules folder, Trivy and cargo audit use the copies they already have, and npm audit, pnpm audit and OSV are skipped.

## Files

`SKILL.md` holds the rules and steps for the agent, and `reference/checklist.md` the security checklist with points for Node, Python, PHP and WordPress, Rust, Luau and Roblox, plus where to look up advisories. `scripts/start.py` takes the snapshot, `scripts/scan.py` runs the scanners and says whether to go on, `scripts/finish.py` cleans up and prints what the report needs; their parts live in `scripts/lib`. `tests/` checks the parts that need no network and no scanner.

## What was tested

These are the real runs, done on this PC on 2026-11-17.

- `python -I -B -m unittest discover -s . -p "test_*.py"` in `tests`: 35 tests pass, and no bytecode is left behind. They cover reading the output of Semgrep, Gitleaks, Trivy, Bandit, gosec, cargo audit, npm audit, pnpm audit and SonarQube from small samples, the lockfile readers and severity rules of the OSV step, merging and finding keys, the stop rule, the growth check, both ledgers, the names of temporary tests, and the cleanup safety rules.
- A small git project in the temporary folder, with planted flaws: SQL built by joining strings, a shell command built from input, a fake token written in the code, `yaml.load`, PyYAML 5.3, lodash 4.17.15 and smallvec 1.6.0. Only cargo audit, npm audit and OSV were available, so the code itself was read against the checklist. The first scan counted 7 blocking findings: the 3 vulnerable packages (smallvec and PyYAML critical, lodash high) and the 4 flaws found by reading. They were fixed with bound parameters, an argument list without shell, an environment variable, `yaml.safe_load`, PyYAML 6.0.3, lodash 4.18.1 through npm and smallvec 1.6.1 through cargo. Three temporary tests were added, 5 tests passed, and the second scan ended on `stop: clean`. The cleanup deleted the 3 temporary tests, the 2 old tests still passed, and the work folder was deleted.
- Web searches on lodash 4.18.1 and PyYAML 6.0.3 found no newer advisory. One of them came back full of copies of an unofficial "advisory tracker" repository, which is why the skill says a forum or an unknown repository proves nothing alone.
- A second run with mistakes planted on purpose: an old test edited, a project file deleted, a temporary file missing from the list, and a list naming a project file, a folder, `.git/config` and a path outside the project, plus two bad ledger lines. The scan reported the edited test and the bad lines and refused to call the result clean. The cleanup put the test and the file back from git, kept the 4 entries it must not delete, and refused to close until the forgotten file was listed. That run was offline: cargo audit read its local database and found nothing left after the fix.
- A test put back by git came back with Windows line endings and was reported as changed again on the next cleanup. Line endings are now ignored when tests are compared, and a third run confirmed it.
- `check_skill.py` of the writing-skills skill on this folder: 0 refused, 0 to check, 0 notes. The strip-ai-traces scan with `--no-git`: 0 fixed, 0 to fix by hand, 0 flagged.

Gaps: Semgrep, Gitleaks, Trivy, Bandit, gosec, pnpm and SonarQube are not installed here, so they were only tested on samples of their output, never for real. cargo audit ran offline only, since its update comes from GitHub. Outside git, files changed after the start join the scope only when they sit in the files or folders named at the start. Not tried on a large project.
