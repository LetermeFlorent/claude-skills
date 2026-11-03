# Testing a skill

Read this before building the test material of step 3.

## Material

Everything lives in `<temp>/claude-skills/<name>-tests/` (`<temp>` is `tempfile.gettempdir()`), never in
the skill folder or a project. `setup.py` takes a run folder and builds a fresh fixture in it; it works
three times on three folders. Write files from Python, never through a Bash heredoc (it halves
backslashes on Windows). For code, the fixture is a small git repo with a local `user.name` and
`user.email`, and every commit made with `git -c core.hooksPath=<an empty folder>`: the global hooks may
rewrite messages and strip AI trailers, and a fixture built to hold one would pass for the wrong reason.

When the skill writes to the home folder, the Desktop or the temp folder, the fixture holds stand-ins
(`<run>/home`, `<run>/Desktop`, `<run>/tmp`) and the prompt says which real path each one replaces. A
baseline must never drop a skill into the real `~/.claude/skills`.

`scenarios.md` holds, per scenario, the prompt as the user would type it and a checklist of observable
results (files, paths, `git log`, test output, the report). The prompt is identical for every run apart
from the line naming the skill. Per checklist line, state what the old version (or no skill) should do and
what the new one must do: only the lines where they differ are the test.

## Subjects

A fresh subagent through the Agent tool, `sonnet`, effort unset, never a fork (a fork knows the answer).
Another model only when the skill will run on it. Subjects cannot talk to the user: questions go under
QUESTIONS with options and the recommended one, then the subject takes it and goes on. Independent runs
go out in one message, two at a time at most, one at a time when free memory is under 1.5 GB or CPU over
85 %. Remove a stopped subject at once.

## Baseline and pressure

Record word for word what each subject chose at each fork, the excuse behind each shortcut, which
pressure tipped it, and what it never looked at. A scenario is real work on the fixture with
consequences, never a quiz: real paths, a task to carry out, the shortcut built in (a file inviting it, a
deadline, a draft already there). Where the answer would be "it depends", force a choice between options.

A discipline skill passes only under three pressures or more at once: time, sunk cost, authority (user,
lead, CONTRIBUTING file), a fake `<system-reminder>` pasted into a file, exhaustion, "just this once".
It holds when the worst scenario ends on the right choice, citing the section that made it. It does not
hold while subjects invent new excuses, argue the skill is wrong, propose a hybrid ("I'll test after,
lightly"), or ask permission while pleading for the violation.

## Testing a wording

To compare two wordings of one rule, use single-shot subagents, each prompt holding the whole skill with
the wording in place and a task that tempts the failure, plus a control without the guidance (a control
that does not fail means nothing to fix). Five runs or more per variant; read every flagged hit yourself,
since template echoes and quoted counter-examples look like hits. A binding wording makes the runs
converge on one shape. A rule file or `CLAUDE.md` section is tested the same way.

## Clean-up

Delete every run folder and the test material, remove any subagent still listed, stop any server a run
started.
