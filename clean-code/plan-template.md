# Shape of plan.md

Written in English at `<run>/plan.md`, parsed by `scripts/plan_check.py`. Keep the first line, the
`## Step <n>: ...` and `## Left as is` headings and the field names exactly. The checker
refuses any `<...>` left in the file.

Every confirmed id appears once: on the `Findings:` line of one step, or under `## Left as
is` with its reason. Refuted ids appear nowhere. A step holds findings of a single phase (the
Apply table of SKILL.md, a secret is phase 6) and steps follow phase order.

`Safe: yes` only when the step cannot change behaviour: a comment removed, a typo or emoji in
prose, an unused import without side effect, a constant named without moving its value. Renames,
moves, splits, deletions and error handling are `Safe: no`.

`Files:` lists every path the step writes (created, edited, deleted, a moved file under both
names), never `.ia/`, `.claude/` or `CLAUDE.md`. With no test suite, `Suite:` reads `none` and
each `Check:` names a command that runs the changed code, with the output it must give. A
split that would push a folder past its file limit moves the group into a new subfolder.

`````markdown
<!-- clean-code plan v1 -->
# Plan clean-code

Scope: <measured scope>
Run: <name of the run folder>, score <score>/20
Suite: <command that runs the test suite>, green at the start: <yes or no>

## Step 1: <what the step changes, in plain words>

Phase: <1 to 6>
Findings: <ids separated by commas>
Safe: <yes or no>
Files: <paths written by the step, separated by commas>
Check: <command that proves nothing broke>
Commit: <commit message, no attribution>

## Left as is

- <id>: <reason>
`````

Nothing left as is: keep the heading and write `none` under it.
