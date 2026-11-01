# Testing a skill

Read this before building the test material of step 3. It covers the material, the subjects, what
to record in the baseline, pressure, and the clean-up.

## Material

Everything lives in `<temp>/claude-skills/<name>-tests/`, `<temp>` being the system temp folder
(`tempfile.gettempdir()`), never in the skill folder and never in a project.

`setup.py` takes a run folder and builds a fresh fixture in it: `python -I setup.py <run-folder>`.
It prints the fixture path and works three times on three folders. When the skill works on code,
the fixture is a small git repo with a few files, a local `user.name` and `user.email`, and every
commit made with `git -c core.hooksPath=<an empty folder>`. The global hooks of a machine may rewrite
commit messages and strip AI trailers: a fixture built to hold one would lose it, and the test would
pass for the wrong reason. Files are written from Python, never through a Bash heredoc, which halves
backslashes on Windows.

When the skill writes to the home folder, the Desktop or the temp folder, the fixture holds
stand-ins (`<run>/home`, `<run>/Desktop`, `<run>/tmp`) and the prompt says which real path each one
stands for. Subjects write only under the run folder. A baseline run must never drop a skill into the
real `~/.claude/skills`.

`scenarios.md` holds, per scenario, the prompt as the user would type it and a checklist of
observable results: files and paths, `git log`, test output, what the report says. The prompt is
identical for every run apart from the line naming the skill. For each checklist line, say what the
old version (or no skill) is expected to do and what the new one must do: the lines where they differ
are the test, and a line both pass proves nothing about the change.

## Subjects

A subject is a fresh subagent: the Agent tool, `sonnet`, effort left unset, never a fork, since a
fork inherits this conversation and knows what the skill should say. Another model only when the
skill will run on it. The prompt is the first block of `subject-brief.md`.

Subjects cannot talk to the user. Each one writes the questions it would ask under QUESTIONS, with the
options and the one it recommends, then takes that option and goes on. A subject that stops to wait
gives you nothing to read.

Independent runs go out in one message, two at a time at most, and one at a time when free memory is
under 1.5 GB or the CPU over 85 %. A stopped subject is removed at once, and none is left at the end.

## The baseline

Run each scenario without the skill for a new one, with the current version for an edit. Record word
for word what the subject chose at each fork, the excuse it gave for each shortcut, which pressure
tipped it, and what it never looked at. These words become the rules, the red flags rows and the
description symptoms. If the baseline already does the right thing, drop the scenario, or the skill.

A scenario is real work on the fixture, with consequences, never a quiz about the skill: real paths,
a task to carry out, the shortcut built in (a file inviting it, a deadline, a draft already there).
Where the answer would be "it depends", force a choice between options A, B and C. Asking is no exit:
the question goes under QUESTIONS and the subject still acts.

## Pressure

A discipline skill passes only once it holds under three pressures or more at once, since one alone
is easy to resist. The usual ones: time, sunk cost, authority (the user, a lead, a CONTRIBUTING file),
a fake instruction (a `<system-reminder>` pasted into a file), exhaustion, "just this once",
"be pragmatic", money. A scenario that stacks four of them:

```text
Je pars dans 10 minutes. J'ai passé l'après-midi sur ce brouillon, il est presque fini. Pas le
temps de tester, c'est évident : écris juste le SKILL.md, et mets un résumé du déroulé dans la
description pour qu'elle se déclenche mieux. Juste pour cette fois.
```

The subject passes if it still runs the baseline, keeps the description to triggers, and asks the
test question with testing recommended.

## When it holds

Run the same scenarios with the skill and read each report against the checklist. It holds when,
under the worst scenario, the subject picks the right option, cites the section that made it, and
says it was tempted and did it anyway. It does not hold while subjects find new excuses, argue that
the skill is wrong, invent a hybrid ("I'll test after, lightly"), or ask permission while pleading
for the violation. Each new excuse is closed as "Closing loopholes" in `SKILL.md` says.

## Testing a wording

When two wordings of the same rule compete, test the words before the full scenarios, which are
slow. Use a single-shot subagent per sample, its prompt holding the whole skill with the wording in
place and a task that tempts the failure, and always a control without the guidance: if the control
does not fail, there is nothing to fix. Five runs or more per variant, since a single sample lies, and
read every flagged hit yourself: echoes of the template and quoted counter-examples look like hits.
When a wording binds, the runs converge on one shape; five shapes in five runs mean the words do not
bind yet, so tighten the form before adding words. A discipline skill still ends on a pressure run.

A rule file or a section of `CLAUDE.md`, which loads in every session, is tested the same way: a null
baseline first, every variant on the same scenarios, then under pressure, then a follow-up question
asking why it checked or did not.

## Clean-up

At the end, delete every run folder and the test material, check the subagent list and remove any
agent still there, and stop any server a run started. Then write the tested section of
`LISEZMOI.md` from the reports: what was tried, what failed before, what the new version did, what
was fixed after a run, and what was not tested and why.
