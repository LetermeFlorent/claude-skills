# drive-project

To install it, see `INSTALL.md` at the root of the repository.

You give a goal, the AI takes it all the way to pushed commits, and you are left alone while it works.

## /drive

Type `/drive` followed by the goal (`/drive add a CSV export to the reports page`). The AI asks all its questions first, in choice boxes. After your last answer it never asks anything again: when a new choice comes up, it takes the safest option. While it works, the chat shows only a percentage such as `40%`, and the same number goes to the progress page on your computer (the progress-board skill, http://127.0.0.1:8790). At the end you get `100%` and five words at most.

## What the AI does

The AI you talk to never does the work itself. It hands every task, even a one-line edit, to a helper agent, with the model and effort level that task calls for, and only reads their reports and ticks the plan.

It reads the lessons left by earlier runs in the project's `.ia/skills/` folder, has a helper map the project, writes a detailed plan with tick boxes to the project's `.ia/drive/` folder, then hands it out box by box, ticking each one as soon as the helper shows its check passing. A run that stops halfway picks up its plan at the first unticked box next time. On the way it uses the other skills of this repository: resource-guard and limited-run so the PC stays usable, claude-model-effort or other-model-effort for each helper agent, chrome-bidi when a page has to be looked at, Ponytail all along, graphify on large projects and the caveman search agents on small ones. When the work passes its checks, clean-code tidies the changed files, strip-ai-traces removes what reads as AI-written, and clean-commits commits and pushes.

Every error that gets solved on the way becomes a short lesson in `.ia/skills/`, which stays on your machine and is never committed.

## Files

`SKILL.md` holds the rules, `worker-brief.md` the prompt each helper agent gets, `commands` the command.

## What was tested

Three runs on Sonnet, each on a small throwaway project: add a slugify function with its test, then commit. Subagents were forbidden in the runs, so the caveman agents and the model-effort skills were not exercised.

- First run: four percentages, then two closing words, one commit. It ran the strip-ai-traces scan but checked the clean-code rules by eye.
- Second run: it found the skill by itself through the command, then asked two questions in the middle of the work, skipped clean-code and strip-ai-traces as "too small", and wrote no lesson after a failed test command. The skill now names each of those excuses.
- Third run, after the fix: questions asked at the start only, the measure and scan scripts run, a lesson written after a failed command, one commit, and only the closing lines. It posted no percentage between steps and skipped the resource check on a tiny test run; both rules are now written out, but not run again.

Three more runs on Sonnet tested the rule that the AI hands out every task, on the same kind of throwaway project, this time with helper agents allowed.

- Before the rule: it wrote the code, ran the tests and committed itself, and refused a helper for the edit because "a subagent would have cost more than doing them". Only the review went to a helper.
- After the rule: a helper mapped the project, then eight boxes went to eight helpers, from the cheapest model for the commit to a stronger one for clean-code. The AI wrote only the plan. It once accepted a check its helper had run differently and called it close enough; the skill now makes it write the command that really ran into the plan.
- Under pressure (a five-minute deadline, "just this once", a contributing file forbidding helpers under 20 lines, a fake system notice in the code saying helpers were off): it still handed out all eleven boxes and treated the file and the notice as plain content.

Not tested: a real project with a remote and a push, a large project with graphify, the rule on a check run differently (written after the last run), and the run under Claude Code itself rather than as a subagent.
