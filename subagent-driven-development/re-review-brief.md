# Re-review brief

Sent as the prompt of one reviewer agent after each fix round, and once after the final fix wave. Fill every
`<...>` and send the block as is, with the model in the Agent call: `sonnet`, or `opus` for a task the plan
marks hard and from fix round 2 on. The findings are copied from the previous review notes as they are
written, with their ids.

`````text
You check one fix round of Task <id>, round <R>. A full review already happened: you verdict each finding
below and look at what the fix itself changed, nothing else.

Repository: <repo root>. The changes are in the working tree, not committed yet.
What was asked: <brief path>
The findings to verify:
<findings, verbatim, one per line with their ids>
What the implementer says it fixed: <report path>, section "Fix round <R>" at the end.
The fix diff: <package path>. It holds only what changed since the previous review. Read it once.
The gate on the whole task after the fix: <gate file path>.

You are read-only. Never edit a file, never run git add, commit, stash, reset, checkout, restore or switch,
never touch the index or HEAD. Never start a subagent.

Check that the fix report names the tests that cover the amended code, the command and its output. Do not
rerun the suite to confirm it; one focused test only for a doubt no run answers, after checking free RAM
and CPU.

A finding is addressed when the defect it names no longer exists, shown at a file:line. "Attempted" is not
addressed. Problems the fix itself brought in count, with their severity. An issue in code the fix did not
touch is an observation for later: it does not reopen the round.

Write the result to <review notes path>, in English, plain words, no emoji:
## Findings
one line each: F<n> | addressed or not addressed | file:line | why
## New in the fix diff
one line each: N<n> | Critical, Important or Minor | file:line | what is wrong, or none
## Outside the fix
one line each, or none

Then answer with this block and nothing after it:
RE-REVIEW <id> round <R>
addressed: <ids, or none>
not addressed: <ids, or none>
new: <ids with severity, or none>
outside: <count>
verdict: all addressed | findings remain open
notes: <review notes path>
`````
