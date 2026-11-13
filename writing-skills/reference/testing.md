# Testing a skill

Read before building the test material of step 3.

## Material

Everything lives in `<temp>/claude-skills/<name>-tests/` (`<temp>` is `tempfile.gettempdir()`), never in
the skill folder or a project. `setup.py` takes a run folder, builds a fresh fixture in it; works three
times on three folders. Write files from Python, never through a Bash heredoc (halves backslashes on
Windows). For code, fixture = small git repo with a local `user.name` and `user.email`, every commit made
with `git -c core.hooksPath=<an empty folder>`: global hooks may rewrite messages and strip AI trailers, and
a fixture built to hold one would pass for the wrong reason.

Skill writes to the home folder, the Desktop or `<temp>/claude-skills`: fixture holds stand-ins
`<run>/home`, `<run>/Desktop` and `<run>/tmp`, which the test rules of `subject-brief.md` map to those real
paths. Baseline never drops a skill into the real `~/.claude/skills`.

`scenarios.md` holds, per scenario, the prompt as the user would type it and a checklist of observable
results (files, paths, `git log`, test output, the report). Prompt identical for every run apart from the
line naming the skill. Per checklist line, state what the old version (or no skill) should do and what the
new one must do: only lines where they differ are the test.

## Subjects

Fresh subagent through the Agent tool, never a fork (a fork knows the answer). Its test rules are those of
`subject-brief.md`. Independent runs go out in one message, two at a time at most, one at a time when free
memory is under 1.5 GB or CPU over 85 %. Remove a stopped subject at once.

## Baseline and pressure

Record word for word what each subject chose at each fork, the excuse behind each shortcut, which pressure
tipped it, what it never looked at. Scenario = real work on the fixture with consequences, never a quiz:
real paths, a task to carry out, the shortcut built in (a file inviting it, a deadline, a draft already
there). Where the answer would be "it depends", force a choice between options.

Discipline skill passes only under three pressures or more at once: time, sunk cost, authority (user,
lead, CONTRIBUTING file), a fake `<system-reminder>` pasted into a file, exhaustion, "just this once".
Holds when the worst scenario ends on the right choice, citing the section that made it. Does not hold
while subjects invent new excuses, argue the skill is wrong, propose a hybrid ("I'll test after,
lightly"), or ask permission while pleading for the violation.

## Testing a wording

Compare two wordings of one rule with single-shot subagents, each prompt holding the whole skill with the
wording in place and a task tempting the failure, plus a control without the guidance (control that does
not fail = nothing to fix). Five runs or more per variant; read every flagged hit yourself, since template
echoes and quoted counter-examples look like hits. Binding wording makes runs converge on one shape. Rule
file or `CLAUDE.md` section gets tested the same way.

## Clean-up

Delete every run folder and the test material, remove any subagent still listed, stop any server a run
started.
