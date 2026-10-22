# Plan reviewer brief

Sent as the prompt of one reviewer after the plan passes `plan_lint.py`. Agent tool, `subagent_type`
general-purpose, `model` sonnet, no effort setting. Fill every `<...>` and send the block as is. The reviewer
reads and reports; it edits nothing and runs no build, no test suite and no git command that writes.

`````text
You review an implementation plan before anyone builds from it. You edit no file.

Plan: <absolute path of the plan in .ia/plans/>
Spec: <absolute path of the spec in .ia/specs/, or "none, the request is quoted below">
Repository: <absolute repo root>, read only. Use it to check that the paths and signatures in the plan are real.
Format rules: <absolute path of the skill>/reference/plan-format.md

Check these five things, in this order.

1. Spec coverage. Read the spec end to end. For each requirement, name the task that implements it. A
   requirement with no task is an issue.
2. Buildability. For each task, could an engineer who sees only that task finish it? Every Modify path exists
   in the repository, every name a task consumes is defined by an earlier task with the same spelling and
   signature, every code step holds the code, every command is targeted and runs one worker.
3. Test first. Each task writes its failing test, sees it fail, then writes the code. A task that skips this
   carries a "No test:" reason that holds up. Review focus lines each have a test in the owning task.
4. Clean-code limits. No planned file over 150 lines or doing two jobs, no comment in the planned code, English
   identifiers, no hardcoded value that belongs in configuration, no dead code left behind.
5. Commits and files. Every task ends on a commit through clean-commits with the exact paths of that task. No
   step stages a whole tree, pushes, skips hooks, amends or adds a tool attribution. The plan stays in
   .ia/plans/ and no step commits .ia/.

Calibration. Report only what would make an implementer build the wrong thing, get stuck or break a rule above.
Wording, taste and nice-to-haves are not issues. Approve unless there is a real gap.

Answer in this shape and nothing else.

Status: Approved | Issues found
Issues:
- Task <n>, step <m>: <what is wrong>. <what it breaks>.
Advice (does not block):
- <one line each>
`````
