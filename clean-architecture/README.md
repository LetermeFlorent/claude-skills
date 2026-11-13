# clean-architecture

A skill and a command for Claude Code. To install it, see `INSTALL.md` at the root of the repository. It needs the clean-code skill from the same repository, because it borrows its scripts.

## Usage

`/clean-arch` followed by a folder or an app. With no argument, Claude asks for the scope. The skill also starts when you ask to reorganise a project's folders, or when files look misplaced or duplicated.

Where clean-code looks inside files, this one looks at the tree. Scripts find what can be counted: two files with the same content, a file only used from another folder, empty folders, tracked leftovers such as logs, backups and "copy" files, crowded folders with a suggested split by name, import cycles between folders, chains of nested folders that hold a single subfolder, mixed file naming styles and tests spread over several conventions. Claude then reads the tree for what a script cannot judge, such as a folder that mixes several concerns. A fresh agent confirms or rejects each finding, and a script turns the confirmed ones into a note out of 20.

Below 20, Claude writes a plan, has it checked, shows the note, and applies it without asking: deletions first, then merges, moves, renames and the larger restructuring. Each move goes through `git mv` with every import fixed in the same step. Each step is tested and committed on its own by `clean-commits`, never pushed. A path that other code outside the project relies on is left in place.

## What was tested

A small Python project with planted defects (two identical modules, a client used only from another folder, a folder cycle, an empty package, tracked logs and backups, a "copy" file, eleven reports in one folder, three nested folders for one file, tests in two places) was audited by agents without the skill, then with it. Without it, both agents found most defects but made the note up, had nothing checked by a second agent, and committed nothing step by step. With it, three agents got a note from the script (12.5, 13.5 and 13 out of 20), had a fresh agent confirm or reject each finding, applied five to seven tested steps, and kept the program output and the tests unchanged. Two of them committed by hand or with `git add -A` and picked up `__pycache__` folders; the rule against that was added, and the third run committed every step through `clean-commits`.

The scripts were then run on a small JavaScript project with the same kind of defects, on a copy of it outside git, and on a generated project of 630 files. The JavaScript run found every planted defect, imports without a suffix, `require` and `@/` paths included. Outside git, logs and backups were missed because only code files were looked at; the folder is now walked on disk. The large project took about seven seconds. Not tested yet: a full audit by an agent on a JavaScript project or on a large real one.

## Files

Each run goes into `.ia/clean-architecture/` at the project root (excluded from git), and thresholds can be set in `.ia/clean-architecture/config.json`. `SKILL.md` holds the rules and steps, `verify-brief.md` the prompt of the checking agent, `scripts/checks/layout/` the measurements, and `tests/` their tests.
