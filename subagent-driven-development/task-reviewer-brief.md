# Task reviewer brief

Sent as the prompt of one reviewer agent after each task's gate. Fill every `<...>` and send the block as is,
with the model in the Agent call (rule 6 of `SKILL.md`). The global constraints are copied from the plan or the
spec as they are written: exact values, formats, the relations between parts ("same layout as X"). Never add a
line that tells the reviewer what not to flag, what severity to give or what the plan chose: a finding you
doubt is raised first and ruled on after.

`````text
You review Task <id> of a plan, one task and nothing wider. A review of the whole branch comes later.

Repository: <repo root>. The task's changes are in the working tree, not committed yet.
What was asked: <brief path>
What the implementer says it did: <report path>. Treat it as claims to check, rationales included: "kept
it simple on purpose" is the implementer grading its own work and lowers no finding.
The diff under review: <package path>. Read it once: it holds the changed files, a stat and the diff with
ten lines of context. Read a changed file in full only when a hunk you must judge is cut, and say so.
The gate: <gate file path>. It lists what the clean-code measure and the anti-empreinte scan found on the
lines this task wrote. Each row there is a finding unless you show it is wrong.
Global constraints that bind this task:
<constraints, verbatim, or none>

You are read-only. Never edit a file, never run git add, commit, stash, reset, checkout, restore or switch,
never touch the index or HEAD. Read-only git (log, show, diff, blame, grep, ls-files) is allowed for a named
risk. Never start a subagent: if the diff is long, review it in passes yourself.

Do not crawl the codebase. Look outside the diff only to check a risk you can name (a changed signature
and its callers, shared state, lock order), one focused check per risk, and name the risk and the check.

The implementer ran the tests and its report holds the output: do not run the suite again. Run one focused
test only when the code raises a doubt no run answers, after checking free RAM and CPU, and never a server, a
build or a docker command. Warnings or noise in the reported output are findings, and output missing from the
report is a gap to report.

Part 1, the spec. Compare the diff with the brief:
- missing: asked and not built, or claimed and not in the diff;
- extra: built and not asked, options nobody needs;
- misunderstood: the right thing built the wrong way, or the wrong problem solved;
- for a batch of files, every listed file has its hunk, or that file is missing.
A requirement that lives in unchanged code or across tasks goes under "cannot verify", with what the
controller should check, instead of a wider search.

Part 2, the build. One job per file, errors not swallowed, duplication of a logic block, edge cases of the
task, tests that go through the public behaviour and assert something, names that say what they hold,
files this change made large. The code rules of clean-code hold: no comment in code, English identifiers,
no hardcoded value, files under 150 lines.

Severity. Critical: wrong results, data loss, a security hole. Important: the task cannot be trusted until
it is fixed: a missed requirement, fragile behaviour, a test that asserts nothing, a duplicated block, an
error turned into a default. Minor: polish, "coverage could be wider". Something the plan itself mandates
and this rubric calls a defect is still a finding, Important, marked plan-mandated: the plan does not grade
itself.

Write the review to <review notes path>, in English, plain words, no emoji, no praise section:
## Spec
compliant, or the issues found, each with file:line
## Cannot verify from the diff
each item and what to check, or none
## Findings
one line each: F<n> | Critical, Important or Minor | file:line | what is wrong | why it matters | the fix
when it is not obvious
## Checks run
each named risk and what you looked at

Then answer with this block and nothing after it:
TASK REVIEW <id>
spec: compliant | issues found
cannot verify: <count>
findings: <n> critical, <n> important, <n> minor
open: <ids of the critical and important findings and spec issues, or none>
verdict: approved | needs fixes
notes: <review notes path>
`````
