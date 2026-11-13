---
name: clean-architecture
description: Use when the user types /clean-arch, asks to audit or reorganise a project's folder layout, or files look misplaced, duplicated or useless, or a folder has become a dumping ground.
---

# Clean architecture

Audit scope's folder layout: misplaced, duplicated, useless files and folders, missing groups, folder cycles.
Note /20 from script on verified findings, then plan, then apply. Same machine as the clean-code skill: its
"Rules that never bend", Apply and Report hold here. Needs clean-code installed next to this folder.

`<skill>` = this folder. Scripts from project root: `python -I "<skill>/scripts/<tool>.py"`. Run goes to
`.ia/clean-architecture/<run>/`, thresholds in `.ia/clean-architecture/config.json`.

## Rules

Defaults in brackets.

0. Bad layout outside grid, 0.5 to 3 points.
1. No two files with same content. Script. Look-alike files: by reading.
2. File lives with its users: used only from one unrelated folder, it moves there, or to a new folder when
   rule 9 says the users' folder is the wrong concern. Script.
3. Nothing useless: folder of empty files, tracked junk (logs, backups, copies, OS files, built output). Script.
4. Folder over `max_files` [8] code files splits by name prefix, `group_min` [3] files a group. Script.
5. No import cycle between folders. Script.
6. No needless depth: chain of folders holding one subfolder only, depth over `max_depth` [6]. Script.
7. One file naming style per folder. Script.
8. Tests in one place, one convention. Script.
9. One folder, one concern: no folder mixing layers or domains (UI, data, clients, models). Reading.
10. Tree fits project kind and framework; root holds entry points, manifests, docs, config only. Reading.

| Rule | Deduction |
|---|---|
| 0 | its points |
| 1, 5 | 1 per finding, 3 at most |
| 2, 3, 4, 9, 10 | 0.5 per finding, 2 at most |
| 8 | 0.5 per finding, 1 at most |
| 6, 7 | 0.25 per finding, 1 at most |

## Audit

Each step ends before next.

1. Scope: `/clean-arch` argument, else `AskUserQuestion`, narrowest folder first.
2. Measure: `measure.py <scope>`.
3. Suite: run project tests once, low priority, two workers at most. Result = plan `Suite:` line.
4. Read: tree (`git ls-files <scope>`), then files the candidates name. Rules 9, 10, 0, look-alike files:
   `findings.py add --rule <n> --file <path> --line <n> --what "<defect>" --proof "<paths or lines>"`.
   Rules 9 and 10 each need a finding or `findings.py checked --rule <n> --why "<what was read>"`, on every
   run, new measure included, else `score.py` refuses.
5. Verify: one fresh Agent call, never a fork, prompt `verify-brief.md`.
6. Score: `score.py`. At 20: stop, no plan.
7. Plan: `<run>/plan.md` shaped like clean-code `plan-template.md`, first line
   `<!-- clean-architecture plan v1 -->`, phases below. `plan_check.py` until `plan ok`.
8. Print note alone as heading, `# 14/20`, then apply whole plan without asking.

## Apply

clean-code Apply section, this phase table:

| Phase | Rules |
|---|---|
| 1 | 0, 3: delete |
| 2 | 1: point every import at kept copy, delete other |
| 3 | 2, 4, 6, 8: move |
| 4 | 7: rename |
| 5 | 5, 9, 10: restructure |

- Finding an earlier step already solves (file merged or deleted, cycle gone): `Left as is`, naming that step.
- Commit through the clean-commits skill with the step's `Files:` only, hurry or not: a hand `git commit`
  skips its checks. Never `git add -A` or a folder: it takes `__pycache__`, `.ia/` and other sessions' files.
- Move = `git mv`, then every import, path string, config entry and doc link fixed in same step.
- Before each commit, `rg` old path and old module path (dotted) in project: no hit left.
- Delete only after `rg` of the name finds no reference.
- Public path (package export, route, URL, file another repo reads) never moves: `Left as is`.

## Report

clean-code Report, after a new measure, verify and score on same scope.

## Files

New check = module in `scripts/checks/layout/` with `check(files, root, config)` returning `(findings, stats)`.
Tests: `python -I -B -m unittest discover -s tests -p "test_*.py"` from this folder.
