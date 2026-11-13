# Shape of plan.md

English, at `<run>/plan.md`, parsed by `scripts/plan_check.py`. Keep first line, `## Step <n>: ...`
and `## Left as is` headings, field names and `Suite:` line exactly. Checker refuses any `<...>` left
in file outside backticks: write code such as `<picture>` or `Promise<void>` between backticks.

Every confirmed id appears once: on `Findings:` line of one step, or under `## Left as is` with its
reason. Refuted ids appear nowhere. Step holds findings of single phase (Apply table of SKILL.md,
secret is phase 6), steps follow phase order.

`Safe: yes` only when step cannot change behaviour: comment removed, typo or emoji in prose, unused
import without side effect, constant named without moving its value. Renames, moves, splits,
deletions and error handling are `Safe: no`.

`Files:` lists every path step writes (created, edited, deleted, moved file under both names), never
`.ia/`, `.claude/` or `CLAUDE.md`. No test suite: `Suite:` reads `none`, each `Check:` names command
that runs changed code, with output it must give. Split that would push folder past its file limit
moves group into new subfolder.

`````markdown
<!-- clean-code plan v1 -->
# Plan clean-code

Scope: <measured scope>
Run: <name of the run folder>, note <note>/20
Suite: <command that runs the test suite>, green at the start: <yes, or no and each failing test or error>

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

Nothing left as is: keep heading, write `none` under it.
