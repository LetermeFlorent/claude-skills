# drive-project

To install it, see `INSTALL.md` at the root of the repository.

You give a goal, the AI takes it all the way to pushed commits, and you are left alone while it works.

## /drive

Type `/drive` followed by the goal (`/drive add a CSV export to the reports page`). The AI asks all its questions first, in choice boxes. After your last answer it never asks anything again: when a new choice comes up, it takes the safest option. While it works, the chat shows only a percentage such as `40%`. At the end you get `100%` and five words at most.

## What the AI does

It reads the lessons left by earlier runs in the project's `.ia/skills/` folder, writes a detailed plan with tick boxes to the project's `.ia/drive/` folder, then does it box by box, ticking each one as soon as its check passes. A run that stops halfway picks up its plan at the first unticked box next time. On the way it uses the other skills of this repository: resource-guard and limited-run so the PC stays usable, claude-model-effort or other-model-effort for each helper agent, chrome-bidi when a page has to be looked at, Ponytail all along, graphify on large projects and the caveman search agents on small ones. When the work passes its checks, clean-code tidies the changed files, strip-ai-traces removes what reads as AI-written, and clean-commits commits and pushes.

Every error that gets solved on the way becomes a short lesson in `.ia/skills/`, which stays on your machine and is never committed.

## Files

`SKILL.md` holds the rules, `commands` the command.

## What was tested

Three runs on Sonnet, each on a small throwaway project: add a slugify function with its test, then commit. Subagents were forbidden in the runs, so the caveman agents and the model-effort skills were not exercised.

- First run: four percentages, then two closing words, one commit. It ran the strip-ai-traces scan but checked the clean-code rules by eye.
- Second run: it found the skill by itself through the command, then asked two questions in the middle of the work, skipped clean-code and strip-ai-traces as "too small", and wrote no lesson after a failed test command. The skill now names each of those excuses.
- Third run, after the fix: questions asked at the start only, the measure and scan scripts run, a lesson written after a failed command, one commit, and only the closing lines. It posted no percentage between steps and skipped the resource check on a tiny test run; both rules are now written out, but not run again.

Not tested: a real project with a remote and a push, a large project with graphify, the caveman agents, and the run under Claude Code itself rather than as a subagent.
