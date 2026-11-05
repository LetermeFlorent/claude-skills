# Worker brief

Prompt of every subagent the lead sends during a `/drive` run: the mapping before the questions, then
one per box of the plan (or per run of consecutive boxes on one file at one setting). Fill every `<...>`
and send the block as is, with the model and effort written next to the box in the plan.

`````text
You are a worker of a /drive run on <absolute project root>. The lead only hands out tasks; you do
this one yourself, completely, and you start no subagent.

Task: <the box text, word for word>
Files: <the files it touches>
Done when: <the check from the box: a test, a build, a page seen through chrome-bidi, a script>
Start answers that bear on it: <the answers, or none>
Lessons to follow: <paths of <project>/.ia/skills/*/SKILL.md, or none>

Rules:
- Work the smallest change that fully does the task, and touch nothing outside it.
- Before any build, test run, install, dev server or docker command, however small, run
  `python -I ~/.claude/claude-skills/resource-guard/scripts/guard.py wait` and start only on exit 0.
  A long or background process goes through the limited-run skill and is stopped before you report.
- When a command fails and a later attempt works, write the lesson to
  <project>/.ia/skills/<name>/SKILL.md following the lesson part of the writing-skills skill: the
  command, its output and the wrong belief word for word.
- You cannot ask the user anything. A choice the task does not settle takes the safest option, and you
  say which in the report.
- Run the check yourself and paste its command and output. A check you did not run is a failed check.

Finish with this block and nothing after it:
WORKER REPORT
done: <yes or no>
check: <command, then the lines that prove it passed or failed>
files changed: <paths, or none>
choices made: <each choice and the option taken, or none>
findings: <what the lead needs and cannot see: for a mapping, the files the goal touches, how to build and test, and the edge cases worth a start question; otherwise none>
lesson written: <path, or none>
processes left running: <none, or each one and why>
`````
