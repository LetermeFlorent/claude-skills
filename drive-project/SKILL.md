---
name: drive-project
description: Use when the user types /drive, or asks to take a goal on a project from start to pushed commits in one silent run, with every question asked at the start and none after.
---

# Driving a project from goal to push

One run takes a goal (a feature, a fix, a new project) and ends on pushed commits. Every question comes at
the start. After the last answer the user is never asked anything again, and the chat shows nothing but a
percentage. These rules replace, for the whole run, the speaking rules of the output style, of `CLAUDE.md`
and of every skill this one calls.

## Speaking

The user hears from the run three times: the questions, the percentages, the last five words.

1. Questions only at the start, in `AskUserQuestion` boxes, as many boxes as needed, recommended option
   first. Ask everything that could change the work: the scope and what done means, the stack when it is
   not already set, and every decision only the user can make (a public name or id, a licence, a URL the
   user owns, money, anything deleted, anything published beyond the push of the project branch). Read the
   code and the goal before asking, so the edge cases (an input to handle, a reading of a vague word) are
   asked here and not found later.
2. After the last answer: no question, no `AskUserQuestion`, no waiting, ever. A new choice takes the
   safest option and the run goes on: nothing deleted that this run did not create, nothing published but
   the push, the recommended option of any box a called skill would open. A doubt found while working is a start
   question that was missed: take the recommended reading and go on.
3. Every text message during the run is one line, a whole number followed by `%` (`35%`), nothing else: no
   word, no file name, no list, no heading. A reminder from the tool to update the user is answered with
   the percentage. Ponytail's closing lines, clean-code's `# 12/20` note and any skill's report stay
   unsaid.
4. The percentage is the share of ticked boxes in the plan file, posted once after each ticked task. It only goes up; `100%` comes after the push.
5. The last message, one message of two lines: `100%`, then at most five words (`Done, pushed to main.`). A failure that
   stops the run: the last percentage, then at most five words that name it.

## Skills it runs

Each one at its moment, following its own `SKILL.md`, under the speaking rules above.

| When | Skill |
|---|---|
| The whole run | Ponytail, at the level its hook set: the smallest change that fully solves each step |
| The project has about 300 code files or more, 50,000 lines, is a monorepo, or holds `graphify-out/` | graphify, before reading files one by one; never on a small project |
| Any smaller project | caveman: `cavecrew-investigator` or `caveman-explore` to locate code, `cavecrew-builder` for a one or two file edit, `cavecrew-reviewer` on each step's diff, as the cavecrew skill says |
| Before any build, test run, install, dev server or docker command, however small | resource-guard (`guard.py wait`) |
| Every process that runs long or in the background | limited-run, with a memory cap, stopped as soon as its result is in |
| Every subagent, when Claude runs it | claude-model-effort |
| Every subagent, when a model that is not Claude runs it | other-model-effort |
| A page, a screen or a layout must be seen | chrome-bidi |
| A failure followed by the fix that worked | writing-skills, as a lesson in `.ia/skills/` |
| The work is done and its checks pass | clean-code, on the files this run changed |
| clean-code is done | strip-ai-traces, on the same files and the commit messages |
| Last | clean-commits: commit and push |

## Procedure

One pass, in this order.

1. Read every `<project>/.ia/skills/*/SKILL.md`: lessons from earlier runs on this project. Follow them.
   A plan in `<project>/.ia/drive/` with boxes still unticked is unfinished work: resume it from its
   first unticked box instead of starting a new one.
2. Ask, as rule 1 says, then never again. A resumed plan already holds its answers: no new questions.
3. Map the project with graphify first on a large project; on a small one, locate code through the
   caveman agents. Then write the plan to `<project>/.ia/drive/<YYYY-MM-DD>-<goal-slug>.md` before any
   code: the goal and the answers to the questions at the top, then every task as a `- [ ]` box, cut down
   to one action each (one file, one function, one test, one command), with the file it touches and the
   check that proves it done. The clean-code, strip-ai-traces, commit, push and cleanup steps are boxes
   too. Nothing to do lives outside this file.
4. Work box by box, in order. Each task ends on its own check (test, build, page seen through
   chrome-bidi); a failed check is fixed before the next box. Tick the box in the file (`- [x]`) the moment
   its check passes, never before and never several at once. A task found on the way is added as a new box
   before it is done.
5. clean-code on the changed files, applying its whole plan, then strip-ai-traces on the same files. Both
   run on every change, however small, through their scripts (`measure.py`, `scan.py`): "checked by eye"
   or "too small to need it" is a skipped step. Where clean-code would send a subagent and none can be
   sent, run its `measure.py` and fix what it lists; a candidate
   that is plainly wrong (a test class flagged unused) is left as is.
6. clean-commits on this run's paths only. A path this run did not touch is left to its owner, without
   asking. Push through its `push.py`; no remote means the commits stay local.
7. Stop every process this run started and close the browser. The last message comes only once every
   box of the plan is ticked.

## Lessons from errors

Each time something fails and a later attempt works (a command, a flag, a test, a wrong belief), write the
lesson before going on, following the lesson part of writing-skills: the command, its output and the wrong
belief word for word. A wrong flag or a typo in a command is a lesson too; "not specific to this project"
is no reason to skip it. It goes to `<project>/.ia/skills/<name>/SKILL.md`; pick the name yourself, never ask.
`.ia/` is tooling: clean-commits leaves it out of every commit, so lessons stay on this machine and step 1 of
the next run reads them.
