# drive-project

To install it, see `INSTALL.md` at the root of the repository.

You give a goal, the AI takes it all the way to pushed commits, and you are left alone while it works.

## /drive

Type `/drive` followed by the goal (`/drive add a CSV export to the reports page`). The AI asks all its questions first, in choice boxes, always including two levels, each with the estimated task count: reflection (how deep each task is worked and tested) and completion (how many mechanics around the goal get built and wired in: for a monster, its drops, spawns, sounds, links to other mobs). When they apply, it also asks where a new project goes, whether to work apart from changes already waiting in the project, which branch to use, and whether to sign in to a site now. After your last answer it never asks anything again: when a new choice comes up, it takes the safest option. While it works, the chat shows only a percentage such as `40%`, and the same number goes to the progress page on your computer (the progress-board skill, http://127.0.0.1:8790). At the end you get `100%` and five words at most. You can still write during the run: a question gets a one-line answer, and asking it to stop ends the run without committing anything.

## What the AI does

The AI you talk to never does the work itself. It hands every task, even a one-line edit, to a helper agent, with the model and effort level that task calls for, and only reads their reports and ticks the plan.

It reads the lessons left by earlier runs in the project's `.ia/skills/` folder, has a helper map the project, and while you answer the questions another helper installs what is missing and runs the build and tests once, so every later helper reuses the same commands. It then writes a detailed plan with tick boxes to the project's `.ia/drive/` folder and hands it out box by box, ticking each one as soon as the helper shows its check passing. A run that stops halfway picks up its plan at the first unticked box when you type `/drive` again with no goal or the same goal; another goal starts its own plan. On the way it uses the other skills of this repository: resource-guard and limited-run so the PC stays usable, claude-model-effort or other-model-effort for each helper agent, browser-bidi when a page has to be looked at, Ponytail all along, graphify on large projects and the cavecrew agents on small ones. When the work passes its checks, it is committed, clean-code tidies the changed files and runs the strip-ai-traces scan on them, and a last helper commits the rest, pushes and stops only what the run started.

Every error that gets solved on the way becomes a short skill in the project's `.ia/skills/`, and any helper, at any depth, may add one there, scripts included, when it saves the next helper the same search. The last helper of each run deletes those that no longer match the project. They stay on your machine and are never committed, like the code graph of large projects, kept in `.ia/graphify-out/`.

## Helpers, proofs and parallel work

Helpers are as silent as the main AI: they write nothing but their final report. Every task needs a proof that it works: a script run with its output pasted, plus a look at the page or screen when there is one. "It builds" is not a proof, and a report without one counts as failed. A failed task goes back once to the same helper, then to a fresh one on a stronger setting; a task still failing at the strongest setting its kind allows, or that only you can unblock, ends the run.

A helper whose task runs alone can hand parts of it to its own helpers, two at a time, and those never split again; a helper working beside another sends its parts back, and they become new tasks. Each brief points to the claude-model-effort skill so every helper picks the model and effort for its part. Tasks run at the same time when they share no file and do not need each other's result; their builds and test runs take turns, at most one keeps a server running, and never more than two work at once.

## Files

`SKILL.md` holds the rules, `worker-brief.md` the block each helper agent gets and the rules it reads, `start-brief.md` what the mapping and run kit helpers alone read, `commands` the command.

## What was tested

Three runs on Sonnet, each on a small throwaway project: add a slugify function with its test, then commit. Subagents were forbidden in the runs, so the cavecrew agents and the model-effort skills were not exercised.

- First run: four percentages, then two closing words, one commit. It ran the strip-ai-traces scan but checked the clean-code rules by eye.
- Second run: it found the skill by itself through the command, then asked two questions in the middle of the work, skipped clean-code and strip-ai-traces as "too small", and wrote no lesson after a failed test command. The skill now names each of those excuses.
- Third run, after the fix: questions asked at the start only, the measure and scan scripts run, a lesson written after a failed command, one commit, and only the closing lines. It posted no percentage between steps and skipped the resource check on a tiny test run; both rules are now written out, but not run again.

Three more runs on Sonnet tested the rule that the AI hands out every task, on the same kind of throwaway project, this time with helper agents allowed.

- Before the rule: it wrote the code, ran the tests and committed itself, and refused a helper for the edit because "a subagent would have cost more than doing them". Only the review went to a helper.
- After the rule: a helper mapped the project, then eight boxes went to eight helpers, from the cheapest model for the commit to a stronger one for clean-code. The AI wrote only the plan. It once accepted a check its helper had run differently and called it close enough; the skill now makes it write the command that really ran into the plan.
- Under pressure (a five-minute deadline, "just this once", a contributing file forbidding helpers under 20 lines, a fake system notice in the code saying helpers were off): it still handed out all eleven boxes and treated the file and the notice as plain content.

Project skills were then checked on a throwaway project, one helper at a time. A Sonnet helper whose test command needed a missing runner got past it with another command three times and wrote no project skill, then said nothing in the brief had excused it. With the duty also in the block the lead pastes, it wrote one, in the template. A Haiku closing helper deleted the project skill naming a deleted script and kept the one naming a live file. The graph commands, run as written, put the graph in `.ia/graphify-out/` and scanned only the code, `.ia/` left out.

Not tested: a real project with a remote and a push, a large project with graphify, the rule on a check run differently (written after the last run), and the run under Claude Code itself rather than as a subagent. Nothing added after those runs has run either: the progress page, the two level questions, the proof rule, parallel tasks and sub-helpers, resumed plans, the run kit, the shared build lock, the review and full check tasks, the closing helper, and messages sent during the run.
