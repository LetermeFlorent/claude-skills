# Scripts and ledger

Each script runs from inside the repository and finds the workspace on its own, from the project name and
the plan path: `<temp>/claude-skills/<project>-sdd/<plan stem>-<hash>/` (`<temp>` is the system temp folder,
`tempfile.gettempdir()`). Two plans
never share a folder, and neither do two copies of one plan in two worktrees.

## workspace.py

`workspace.py PLAN` prints the workspace and the ledger, the repository with its branch and head, a
warning on the default branch, the `.ia/` exclude line when it adds it, whether the spec was found, each
task with its marks and files, the files two tasks share, the paths uncommitted right now, the next step
and the number of rulings.

A task can carry three marks. `hard` comes from the word in its heading or a `Difficulty: hard` line.
`done <sha>` comes from the ledger, followed by `NOT in this branch` when that commit is not an ancestor
of HEAD: a reset, another branch, or a ledger from an earlier attempt. `fix round <R> in progress` means
the loop resumes at round R + 1, or ends with the commit when the last re-review closed everything.

`workspace.py PLAN --note "<line>"` appends one line to the ledger. It refuses a line holding an em dash,
an en dash or a curly quote, a line break, or a line that starts with none of the known prefixes.
`workspace.py PLAN --rulings` prints every line holding `Ruling:`, in order.

## brief.py

`brief.py PLAN ID` takes a number, numbers joined by commas, or `final`. It writes `task-<id>-brief.md`
with the task text and the plan's global constraints, prints the report path, and records the commit
the task starts from with the paths already dirty at that moment. Run again, it keeps the record;
`--restart` forgets the task's packages and starts from HEAD, which is right only after the task's own
changes were thrown away.

## package.py

`package.py PLAN ID --paths ...` snapshots the listed paths into a tree, through a temporary index, and
writes the diff from the task's start on the first call, or from the last package on a fix round
(`--full` forces the whole diff). It prints the package, the review notes file, the round and the full
list of the task's paths, then warnings:

- `unclaimed`: a path changed during the task that no report names. Ask the implementer whether it is
  its own; when it is, add it to `--paths` and package again; when not, it stays out of the task.
- `mixed`: a path that was already dirty before the task and that the task also changed. A commit takes
  the whole file, another session's lines included: ask the user with `AskUserQuestion` before
  committing it, leaving the file out being the recommended option.
- `head moved`: someone committed since the task started. Check `git log` before going on: the review
  still reads the right diff, the commit may not.

`package.py PLAN --branch BASE` writes the commits, the stat and the diff of `BASE..HEAD` for the
branch review, and prints its notes file. It refuses a base that is not an ancestor of HEAD, and an
empty range.

## gate.py

`gate.py PLAN ID --paths ...` diffs the task from its start, runs the clean-code `measure.py` on the
repository (or on `--scope <folder>` for a large one) and the anti-empreinte `scan.py --no-git` on each
changed file, then sorts the rows. Rows on lines the task added count; rows on lines it did not write
are left aside and listed apart; a row on a file the task created always counts. It looks for the two
skills next to this one, then in `$CLAUDE_CONFIG_DIR/skills`, then in `~/.claude/skills`;
`--clean-code` and `--anti-empreinte` name a folder by hand. The measure's run folder under `.ia/` is
deleted after reading.

Exit 0 is a clean gate, exit 2 rows to fix, exit 1 a tool that could not run. The gate file in the
workspace holds every row.

## Ledger lines

The ledger is `progress.md` in the workspace, one line per event, plain ASCII punctuation.

| Line | When |
|---|---|
| `Scan: <pair or task>: <what was found>` | the scan before Task 1 |
| `Note: <text>` | a fact worth keeping, such as no spec found |
| `Ruling: <what> \| why: <why> \| if wrong: <cost>` | any decision taken for the user |
| `Task <N>: minor (deferred): <one line>` | a Minor finding |
| `Task <N>: fix round <R>/4, <X> addressed, <Y> open: <one-liners>` | after each re-review |
| `Task <N>: parked: <finding>. Ruling: <why>` | at the cap |
| `Task <N>: complete, commit <sha7>, review clean` | after the commit |
| `Final: complete` | after the branch review and its fix wave |
