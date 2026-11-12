---
name: drive-project
description: Use when the user types /drive, or asks to take a goal on a project from start to pushed commits in one silent run, with every question asked at the start and none after, the session only handing tasks to subagents.
---

# Driving a project from goal to push

One run takes a goal (a feature, a fix, a new project) and ends on pushed commits. Every question comes at
the start. After the last answer the user is never asked anything again, and the chat shows nothing but a
percentage. These rules replace, for the whole run, the speaking rules of the output style, of `CLAUDE.md`
and of every skill this one calls.

## The lead hands out every task

The session that runs `/drive` is the lead. It never does the project's work: every task, however small,
goes to a subagent, and the lead only hands out tasks, reads reports and ticks boxes.

1. The lead's own actions are these and no others: read the lessons and the plan file, ask the start
   questions, write and update the plan file and the project skills (Project skills), start subagents,
   read their reports, tick boxes, post the
   percentage in the chat and send it to the progress board (one `curl`, the progress-board skill). It never edits a project file, never runs a build, a test, a script, a git command or a
   browser, and never reads the code: a first worker maps the project for the questions and the plan.
2. Each box goes to one fresh worker, prompt from `worker-brief.md`; consecutive boxes on the same file at
   the same setting may share one. Next to each box the plan writes the model and effort the
   claude-model-effort skill gives its task (other-model-effort when the model is not Claude), starting at
   the row's minimum, and the call sets them.
   Boxes run at the same time when they do not get in each other's way: no file in common, neither needs
   the other's result, and at most one of the two runs a heavy command (build, test run, docker, dev
   server). Never more than two workers working at once across the whole tree, a worker waiting on its
   own sub-workers not counting. The plan marks each box `after: <ids>` or `with: <ids>`; a box with
   neither goes alone. For this run, that replaces the rule keeping builds in the main session.
   A worker may split its box into sub-tasks and hand them to sub-workers, as `worker-brief.md` says,
   to a depth of three below the lead. Every brief names the effort skill's path
   (`~/.claude/claude-skills/claude-model-effort/SKILL.md`, or `other-model-effort` for a model that is
   not Claude) so each sub-worker gets its model and effort from it.
3. A box is ticked only when the report shows its check passing, command and output pasted. No pasted
   check, or a failed one: the same box goes out again, one step up as claude-model-effort's rule 6 says.
   A worker that ran a different check than the box's: the lead writes the command that ran into the box
   before ticking it; "close enough" left unwritten is a skipped check.
4. Every box carries a mandatory proof that the thing works, at every reflection level, *peu* included,
   and for every worker at every depth. The worker first reads the code and the result it must change
   until it can say what it does (understand), then runs the check (test), then looks at the real
   outcome (see). The proof is a script run with its output pasted, a visual proof (the page seen
   through chrome-bidi, the app or game run, a screenshot looked at), or both when the result can be
   seen. "It builds", "it looks right in the code" and "should work" are no proof. The report pastes the
   proof and one line saying what was understood. A box without its proof written in the plan is not
   handed out; a report without it is a failed check. A worker that split its box checks each
   sub-report's proof itself and adds its own proof for the whole.
5. "A subagent would cost more than doing it", "three small edits", "it is one line", "I already have the
   context", "just this once to save time": each is the excuse this rule exists for. The box goes to a
   worker at its row's minimum.

## Speaking

The user hears from the run three times: the questions, the percentages, the last five words.

1. Questions only at the start, in `AskUserQuestion` boxes, as many boxes as needed, recommended option
   first. Ask everything that could change the work: the scope and what done means, the stack when it is
   not already set, and every decision only the user can make (a public name or id, a licence, a URL the
   user owns, money, anything deleted, anything published beyond the push of the project branch). Read the
   goal and the mapping worker's report before asking, so the edge cases (an input to handle, a reading of
   a vague word) are asked here and not found later.
   Two boxes are always asked, never skipped, each with the options *peu*, *moyen*, *beaucoup*, *max*
   (Other stays open for a custom level), and each box's text states the task count the mapping worker
   estimated for the goal:
   - **Reflection level** (depth, per task): how hard each task is worked. *peu*: the smallest change and
     its one check. *moyen*: plus the edge cases and a test. *beaucoup*: plus the design thought through,
     several tests, a review. *max*: the best model and effort on every box, the logic and any AI or
     algorithm worked carefully, tested in many cases and seen running. Example: for a monster, the
     intelligence and the model are polished and tested.
   - **Completion level** (breadth, around the goal): how much that touches the goal gets built with it.
     *peu*: the goal alone. *moyen*: the direct neighbours. *beaucoup*: the mechanics clearly tied to it.
     *max*: every mechanic the mapping worker found that connects to the goal, each one wired in.
     Example: for a monster, its drops, loot table, spawn rules, sounds, sprites, effects, achievements,
     links to other monsters and items.
2. After the last answer: no question, no `AskUserQuestion`, no waiting, ever. A new choice takes the
   safest option and the run goes on: nothing deleted that this run did not create, nothing published but
   the push, the recommended option of any box a called skill would open. A doubt found while working is a start
   question that was missed: take the recommended reading and go on.
3. Every text message during the run is one line, a whole number followed by `%` (`35%`), nothing else: no
   word, no file name, no list, no heading. A reminder from the tool to update the user is answered with
   the percentage. Ponytail's closing lines, clean-code's `# 12/20` note and any skill's report stay
   unsaid. Workers and sub-workers are silent too: their only text outside the final report block is one
   line, a number and `%` for how far their own task is, nothing else.
4. The percentage is the share of ticked boxes in the plan file, posted once after each ticked task. It only goes up; `100%` comes after the push.
   Each time, the same number goes to the progress board, under the project folder's name, as the
   progress-board skill says; `0` goes there as soon as the plan file is written.
5. The last message, one message of two lines: `100%`, then at most five words (`Done, pushed to main.`). A failure that
   stops the run: the last percentage, then at most five words that name it.

## Skills it runs

Each one at its moment, run by the worker whose box needs it, following its own `SKILL.md`, under the
speaking rules above.

| When | Skill |
|---|---|
| The whole run | Ponytail, at the level its hook set: the smallest change that fully solves each step |
| Each percentage, from `0` to `100` | progress-board, read before the first one: the lead sends it to the local page |
| The project has about 300 code files or more, 50,000 lines, is a monorepo, or holds `graphify-out/` | graphify, run by the mapping worker before reading files one by one; never on a small project |
| Any smaller project | caveman: the mapping worker is a `cavecrew-investigator`, a one or two file edit box goes to a `cavecrew-builder`, each step's diff to a `cavecrew-reviewer`, as the cavecrew skill says |
| Before any build, test run, install, dev server or docker command, however small | resource-guard (`guard.py wait`) |
| Every process that runs long or in the background | limited-run, with a memory cap, stopped as soon as its result is in |
| Every worker, when Claude runs it | claude-model-effort |
| Every worker, when a model that is not Claude runs it | other-model-effort |
| A page, a screen or a layout must be seen | chrome-bidi |
| A failure followed by the fix that worked, or a step the next agent would have to work out again | a project skill in `.ia/skills/`, as Project skills says, never through writing-skills |
| The work is done and its checks pass | clean-code, on the files this run changed |
| clean-code is done | strip-ai-traces, on the same files and the commit messages |
| Last | clean-commits: commit and push |

## Procedure

One pass, in this order. From step 2 on, every action is a worker's.

1. Read the progress-board skill, then every `<project>/.ia/skills/*/SKILL.md`: lessons from earlier runs on this project. Follow them
   and hand their paths to every worker. A plan in `<project>/.ia/drive/` with boxes still unticked is
   unfinished work: resume it from its first unticked box instead of starting a new one.
2. Send the mapping worker with the goal: graphify on a large project, a `cavecrew-investigator` on a
   small one. Its report gives the files the goal touches, how to build and test, the edge cases, an estimated task
   count, and the list of mechanics around the goal that connect to it (candidates for the completion level).
3. Ask, as rule 1 of Speaking says, then never again. A resumed plan already holds its answers: no new
   questions.
4. Write the plan to `<project>/.ia/drive/<YYYY-MM-DD>-<goal-slug>.md` before any code: the goal and the
   answers to the questions at the top, with the reflection and completion levels on their own lines. The
   completion level sets which connected mechanics become boxes; the reflection level raises the minimum
   model and effort of every box and adds the test, review and in-game or on-screen proof boxes it calls for, then every task as a `- [ ]` box, cut down to one action each (one
   file, one function, one test, one command), with the file it touches, the check that proves it done
   the proof, the model and effort of its worker, and its `after:` or `with:` ids. The clean-code,
   strip-ai-traces, commit, push and cleanup steps are boxes too. Nothing to do lives outside this file.
5. Hand out the boxes in plan order, together when rule 2 of the lead allows it. Tick a box in the file
   (`- [x]`) the moment its report shows its proof passing, never before; a failed check goes out again
   before any box that comes after it. A
   task found on the way, in a report or otherwise, is added as a new box before it is handed out.
6. The clean-code worker applies the whole clean-code plan on the changed files, then the strip-ai-traces
   worker runs on the same files. Both run on every change, however small, through their scripts
   (`measure.py`, `scan.py`): "checked by eye" or "too small to need it" is a skipped step. Where
   clean-code would send a subagent and the worker cannot, it runs `measure.py` and fixes what it lists; a
   candidate that is plainly wrong (a test class flagged unused) is left as is.
7. The commit worker runs clean-commits on this run's paths only. A path this run did not touch is left
   to its owner, without asking. It pushes through `push.py`; no remote means the commits stay local.
8. The cleanup worker stops every process this run started, closes the browser and tidies
   `<project>/.ia/skills/` as Project skills says. The last message
   comes only once every box of the plan is ticked.

## Project skills

Any agent of the run, the lead, a worker or a sub-worker at any depth, may write a skill for this
project in `<project>/.ia/skills/<name>/SKILL.md`, with its scripts in `<name>/scripts/` when a script
does the job better than text. It must write one each time something fails and a later attempt works (a
command, a flag, a test, a wrong belief, a typo, or a box's failed `Earlier attempt`), before going on,
with the command, its output and the wrong belief word for word. It may write one at any other time a
step it worked out would save the next agent the same search on this project. Each one serves a real
task on this project: its `Use when` line names the command, file or error it is for, and a note about
this run is no skill. "Not specific to this project" is no reason to skip one: for this run every
project skill goes to `<project>/.ia/skills/`, in place of any folder the user's instructions name. The
agent picks the name, never asks, and updates a skill that covers the same thing instead of writing a
second one. A skill found wrong or useless (the file, script or command its `Use when` line names is
gone, or another skill covers it) is deleted by the agent that finds it, which reports it.

The closing worker tidies the folder at the end of every run: it deletes each skill whose `Use when` line
names a file, script or command the project no longer has (checked with `ls` or `rg`), merges two that
cover the same thing into one, and lists each folder it deleted or merged under `files changed`. `.ia/`
is tooling: clean-commits leaves it out of every commit, so project skills stay on this machine and step
1 of the next run reads them.
