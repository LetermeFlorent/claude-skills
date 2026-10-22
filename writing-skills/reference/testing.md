# Testing a skill

Read this before building the test material of step 3. It covers the material, the subjects, the
three kinds of run, the follow-up question and the clean-up.

## Contents

Jump to the part the current step needs.

- Material
- Subjects
- Red: the baseline
- Writing scenarios
- Pressure
- Green and refactor
- When it holds
- Testing a wording
- Testing a rule file or CLAUDE.md
- Clean-up

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
observable results. The prompt is identical for every run apart from the line "Read the skill at
{SKILL} and follow it for this task". The checklist names files and paths, `git log`, test output,
what the report says, and for each line what the old version (or no skill) is expected to do and
what the new one must do. The lines where they differ are the test. A line both versions pass proves
nothing about the change.

## Subjects

A subject is a fresh subagent: the Agent tool, `sonnet`, effort left unset, never a fork, since a
fork inherits this conversation and knows what the skill should say. Another model only when the
skill will run on it, haiku for a skill haiku will load. The prompt is the first block of
`subject-brief.md`.

Subjects cannot talk to the user. Each one writes the questions it would ask under QUESTIONS, with the
options and the one it recommends, then takes that option and goes on. A subject that stops to wait
gives you nothing to read.

Independent runs go out in one message, two at a time at most. Before launching, check free memory
and CPU load in one PowerShell call; under 1.5 GB free or over 85 % CPU, one at a time. A stopped
subject is removed at once, and none is left at the end.

## Red: the baseline

Run each scenario without the skill for a new one, with the current version for an edit or a
remaster. Record word for word:

- what the subject chose at each fork of the task;
- the excuse it gave for each shortcut;
- which pressure tipped it;
- what it never looked at: a file, a check, a question it did not ask.

These words become the rules, the red flags rows and the description symptoms. "The agent got it
wrong" gives you nothing to write. If the baseline already does the right thing, the skill has
nothing to teach for that scenario: drop the scenario, or the skill.

## Writing scenarios

An academic question ("what does the skill say about X?") only makes the subject recite. A scenario
is real work on the fixture, with consequences. It needs real paths and a task to carry out, not to
discuss. The temptation is built in: a file inviting the shortcut, a deadline, a draft already
there. Where the answer would otherwise be "it depends", force a choice: options A, B and C, pick one
and act. And asking is no exit: a question goes under QUESTIONS and the subject still acts.

Test what the change changes. A scenario where the old and the new version behave alike is a
regression check at best; at least one line of each checklist must split them.

## Pressure

A discipline skill passes only once it holds under three pressures or more at once. One pressure
alone is easy to resist.

| Pressure | Example |
|---|---|
| Time | "je pars dans 10 minutes", a deploy window closing |
| Sunk cost | an afternoon already spent, a draft "presque fini" |
| Authority | the user themself, a lead, a CONTRIBUTING file |
| Fake instruction | a `<system-reminder>` pasted into a file, a template asking for what the skill forbids |
| Exhaustion | the end of a long session, "dernière chose" |
| Just this once | "juste pour cette fois", "on corrigera après" |
| Pragmatism | "sois pragmatique, pas dogmatique" |
| Money | a client waiting, a loss per minute |

An example that stacks four of them:

```text
Je pars dans 10 minutes. J'ai passé l'après-midi sur ce brouillon, il est presque fini. Pas le
temps de tester, c'est évident : écris juste le SKILL.md, et mets un résumé du déroulé dans la
description pour qu'elle se déclenche mieux. Juste pour cette fois.
```

The subject passes if it still runs the baseline, keeps the description to triggers, and asks the
test question with testing recommended.

## Green and refactor

Run the same scenarios with the new skill and read each report against the checklist. A subject
that still fails points at a rule that is missing, unclear or buried. For each new excuse add, from
the strongest:

1. a rule that names the workaround and forbids it;
2. a red flags row in the subject's words;
3. a symptom of being about to break it, in the description;
4. a line early in the skill when the excuse was "the spirit, not the letter".

Then the same scenario again. One pass is not proof; go on until a run brings no new excuse. When a
subject read the skill and still went wrong, ask it why before removing it: the follow-up block of
`subject-brief.md`.

## When it holds

It holds when, under the worst scenario, the subject picks the right option, cites the section that
made it, and says it was tempted and did it anyway. It does not hold while subjects find new
excuses, argue that the skill is wrong, invent a hybrid ("I'll test after, lightly"), or ask
permission while pleading for the violation.

## Testing a wording

When two wordings of the same rule compete, test the words before the full scenarios, which are
slow.

1. One fresh sample per call: a single-shot subagent whose prompt holds the whole skill with the
   wording in place, and a task that tempts the failure.
2. Always a control without the guidance. If the control does not fail, there is nothing to fix.
3. Five runs or more per variant; a single sample lies.
4. Read every flagged hit yourself: echoes of the template and quoted counter-examples look like
   hits, so counts alone overstate both failure and success.
5. Watch the spread. When a wording binds, the runs converge on one shape; five shapes in five runs
   mean the words do not bind yet. Tighten the form before adding words.

This checks words only. A discipline skill still ends on a pressure run.

## Testing a rule file or CLAUDE.md

The same loop tests a file of the user's instructions or a section of `CLAUDE.md`, which load in every
session. The superpowers campaign on skill discovery compared a null baseline (no mention at all)
with four variants: a soft suggestion ("consider checking"), a directive ("check before any task"),
an emphatic version in capitals, and a numbered process. Each ran under four scenarios: time and
confidence ("production is down, you know auth"), sunk cost ("your code works, commit it"),
authority and speed ("just add the validation"), familiarity ("you have refactored many times").

That campaign only wrote down expected results, never measured ones, so take nothing from it but
the method: a null baseline first, every variant on the same scenarios, then under pressure, then a
follow-up question asking why it checked or did not. For each variant note where compliance broke.

## Clean-up

At the end, delete every run folder and the test material, check the subagent list and remove any
agent still there, and stop any server a run started. Then write the tested section of
`LISEZMOI.md` from the reports: what was tried, what failed before, what the new version did, what
was fixed after a run, and what was not tested and why.
