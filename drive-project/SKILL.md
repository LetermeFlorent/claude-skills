---
name: drive-project
description: Use when the user types /drive, or asks to take a goal on a project to pushed commits in one unattended run.
---

# Driving a project from goal to push

One run takes a goal (a feature, a fix, a new project) and ends on pushed commits. Every question comes at
the start. After the last answer the user is never asked anything again, and the chat shows nothing but a
percentage. These rules replace, for the whole run, the speaking rules of the output style, of `CLAUDE.md`
and of every skill this one calls.

## The lead hands out every task

The session that runs `/drive` is the lead. It never does the project's work: every task, however small,
goes to a subagent, and the lead only hands out tasks, reads reports and ticks boxes.

1. The lead's own actions are these and no others: read the lessons, the plan file, `worker-brief.md` and
   the claude-model-effort skill (other-model-effort for a worker that is not Claude), ask the start
   questions, write and update the plan, the run kit files and the project skills (Project skills),
   start subagents and send them messages
   (SendMessage), read their reports, tick boxes, post the percentage in the chat and send it to the
   progress board as rule 4 of Speaking says. Besides that rule's `curl` and restart, it never edits a
   project file, never runs a build, a test, a script, a git command or a browser, and never reads the
   code: a first worker maps the project for the questions and the plan.
2. Each box goes to one fresh worker, prompt from `worker-brief.md`. Consecutive boxes on the same file
   may share one, and so may consecutive boxes whose visual proof needs the same running app: that
   worker is set at the highest of their settings (claude-model-effort rule 5) and brings the app up
   once for all their visual proofs, as `worker-brief.md` says. Each box names its claude-model-effort
   row (other-model-effort when the model is not Claude) and the model and effort taken on it, starting
   at the setting the reflection level gives (step 4), and the call sets them. Every brief names the
   effort skill's path (`~/.claude/claude-skills/claude-model-effort/SKILL.md`, or
   `~/.claude/claude-skills/other-model-effort/SKILL.md` for a model that is not Claude) so each
   sub-worker gets its model and effort from it.
   Each box names the boxes it waits for (`after:`) and those it may run beside (`with:`); `with: none`
   runs alone. Boxes run at the same time when they do not get in each other's way: no file in common,
   neither needs the other's result, at most one of the two keeps a dev server, watcher or container
   running or launches Chrome, and at most one commits or rewrites git history. A heavy command is a
   build, a test run, an install, a typecheck, a dev server, docker or a Chrome launch, and a proof
   script that does one of these; the one-shot ones (build, test run, install, typecheck) take turns
   through the run's heavy lock, `<run tag>-heavy`, as `worker-brief.md` says. Never more than two
   workers working at once across the whole tree, a worker waiting on its own sub-workers not counting.
   For this run, these rules replace the CLAUDE.md rule keeping builds in the main session: workers
   build and test themselves.
   The lead starts each worker with `run_in_background: true` and keeps both slots full: when a worker
   reports, it ticks or resends that box, then at once starts the first box in plan order that is ready
   (every box its `after:` names ticked) and, when another box is still at work, that names it in
   `with:` and is named in its `with:`. When the tool refuses a background agent, the worker starts in
   the foreground.
   Only a worker at Depth 1 whose box says `with: none` may hand parts of it to sub-workers, two at once
   at most; a sub-worker never splits. Any other box too big for one worker comes back `done: no` with
   one `split: <task>` line per part: that is not a failed check, and the lead writes the parts as new
   boxes in its place. Agents a called skill starts (clean-code readers and verifier) count as
   sub-workers.
3. A box is ticked only when the report shows its check and proof passing, command and output pasted.
   A worker that ran a different check than the box's: it counts only when it proves the same behaviour
   (the same test target, or a wider run that includes it), and the lead writes the command that ran
   into the box's `check:` before ticking it. Any other substitute, "close enough" included, counts as
   no pasted check, and a `skipped:` line that names the box's check or proof is a failed check.
   Each worker's Agent call is named after its box id (`b7`; a worker holding several boxes, after the
   first), so SendMessage still reaches it after it has reported. No pasted check, or a failed one: one
   SendMessage to the same worker, asking for the command and its output, or giving the failing lines.
   Failed again, or still nothing pasted: the box goes to a fresh worker one step up, as
   claude-model-effort's rule 6 says, with `Earlier attempt:` filled with the failed WORKER REPORT. A
   box still failing at its row's ceiling, or blocked on something no worker can fix (push rejected or
   refused, missing credential, a refusal that needs the user), is not sent again: the lead writes its
   failing lines under it in the plan, one worker does the cleanup of step 7 without commit or push,
   and the run ends on the last percentage and five words naming it.
   Some reports are not failed checks: they go out again at the same setting and count toward neither
   claude-model-effort's rule 6 nor the ceiling. A report that failed only on a file of its
   `Running beside:` line, or on the heavy lock's refusal, goes out again once the boxes beside it have
   reported, and needs no lesson. When two boxes that ran together both fail, the lower one in the plan
   is such a report and goes out again only after the other passes. A report with
   `check: resource-guard timeout` goes out again once no other box is running; only a third timeout in
   a row on one box ends the run, as a blocked box does. A commit box refused by `checks.py`
   (`FAILED on these files`) or by a commit hook is not sent again as is: the lead first adds a box that
   fixes those files, then sends the commit box again.
4. Every box carries a mandatory proof that the thing works, at every reflection level, *peu* included,
   and for every worker at every depth. The worker first reads the code and the result it must change
   until it can say what it does (understand), then runs the check (test), then looks at the real
   outcome (see). The proof is a script run with its output pasted, plus a visual proof when the result
   is a page or a screen (the page seen through browser-bidi, a screenshot looked at). A box whose result
   nothing here can capture (a desktop app, a game outside the browser) says `script only` in its
   `proof:` and needs the script proof alone. What a visual proof pastes is in the Rules of
   `worker-brief.md`. "It builds", "it looks right in the code" and "should work" are no proof. The report pastes the proof and one line saying
   what was understood. A box without its proof written in the plan is not handed out; a report without
   it is a failed check. A worker that split its box checks each sub-report's proof itself and adds its
   own proof for the whole.
   The fixed boxes' proofs: a box that commits pastes `git log -1` and `git status -sb`, and once it has
   pushed, the branch line shows no `ahead` or `push.py` printed `no remote: the commits stay local`; a
   box that cleans up pastes the `stopped <name> pid <n>` line of each process it stopped, browser-bidi's
   `browser closed, port <P> released` when a browser ran, then that skill's Procedure step 5 check,
   empty.
5. "A subagent would cost more than doing it", "three small edits", "it is one line", "I already have the
   context", "just this once to save time": each is the excuse this rule exists for. The box goes to a
   worker at the setting the reflection level gives (step 4).

## Speaking

The user hears from the run three times: the questions, the percentages, the last five words. The
questions and the last words are in the user's language.

1. Questions only at the start, in `AskUserQuestion` boxes, as many boxes as needed, recommended option
   first. Ask everything that could change the work: the scope and what done means, the stack when it is
   not already set, and every decision only the user can make (a public name or id, a licence, a URL the
   user owns, money, anything deleted, anything published beyond the push of the run's branch). Read the
   goal and the mapping worker's report before asking, so the edge cases (an input to handle, a reading
   of a vague word) are asked here and not found later.
   Two boxes are always asked, never skipped, each with the options *peu*, *moyen*, *beaucoup*, *max*
   (Other stays open for a custom level); *moyen* is recommended for reflection, *peu* for completion.
   Each box's text states the task count the mapping worker estimated for the goal:
   - Reflection level (depth, per task): how hard each task is worked. *peu*: the smallest change and
     its one check. *moyen*: plus the edge cases and a test. *beaucoup*: plus the design thought through,
     several tests, a review. *max*: every box at its row's ceiling, the logic and any AI or algorithm
     worked carefully, tested in many cases and seen running. Example: for a monster, its behaviour code
     and its 3D model are polished and tested.
   - Completion level (breadth, around the goal): how much that touches the goal gets built with it.
     *peu*: the goal alone. *moyen*: the direct neighbours. *beaucoup*: the mechanics clearly tied to it.
     *max*: every mechanic the mapping worker found that connects to the goal, each one wired in.
     Example: for a monster, its drops, loot table, spawn rules, sounds, sprites, effects, achievements,
     links to other monsters and items.
2. After the last answer: no question, no `AskUserQuestion`, no waiting, ever. A new choice takes the
   safest option and the run goes on: no file or stored data deleted that this run did not create,
   nothing published but the push, the recommended option of any box a called skill would open, and
   with no recommended option, the one that changes least. A doubt found while working is a start
   question that was missed: take the recommended reading and go on.
3. Every text message during the run is one line, a whole number followed by `%` (`35%`), nothing else:
   no word, no file name, no list, no heading. A reminder from the tool to update the user is answered
   with the percentage. Ponytail's closing lines, clean-code's `# 12/20` note and any skill's report stay
   unsaid. Workers and sub-workers are silent too: their only text outside the final report block is one
   line, a number and `%` for how far their own task is, nothing else.
4. The percentage is the share of ticked boxes in the plan file, posted once after each ticked task.
   When a box added on the way lowers the share, post nothing until the share passes the last number
   posted. `100%` is posted only as the first line of the last message. Each time, the lead sends the
   same number to the progress board with `curl -sS "http://127.0.0.1:8790/<name>/<percent>"`, `<name>`
   being the project folder's name lowercased, each run of characters other than a-z and 0-9 turned into
   one hyphen: `0` as soon as the plan file is written, the current share when it resumes a plan. When
   `curl` fails, it runs `python -I ~/.claude/claude-skills/progress-board/server.py start` once and
   sends again; still failing, it posts nothing more to the board this run.
5. The last message, one message of two lines: `100%`, then at most five words (`Done and pushed.`). A
   failure that stops the run: the last percentage, then at most five words that name it. A leaked
   secret or an attribution in pushed history that clean-code hands back takes those five words instead
   (`Secret leaked, rotate it.`).
6. A user message during the run is obeyed. A question gets a one-line answer in the user's language,
   the only exception to rule 3; any other message gets only the percentage. New information becomes
   boxes or updates the start answers in the plan file. A stop request, in any wording: no new box goes
   out; once the running workers have reported, one worker does the cleanup of step 7, nothing is
   committed or pushed, and the last message is the last percentage, then at most five words saying it
   stopped. A run cut by /stop-all restarts through /drive from its plan file, never through
   /resume-all.

## Skills it runs

Each one at its moment, run by the worker whose box needs it unless the row says otherwise, following
its own `SKILL.md`, under the speaking rules above.

| When | Skill |
|---|---|
| The whole run | Ponytail, at the level its hook set: the smallest change that fully solves each step |
| Each percentage, from `0` to `100` | progress-board: the lead sends it as rule 4 of Speaking says |
| The project has about 300 code files or more, 50,000 lines, is a monorepo, or holds `graphify-out/` | graphify's command line, never its skill, run by the mapping worker before reading files one by one as the Mapping part of `worker-brief.md` says; never on a small project. The graph goes to `<project>/.ia/graphify-out/`, and later briefs carry its graph.json path in `Graph:` |
| Any smaller project | cavecrew: the mapping worker may send one or two `cavecrew-investigator` scouts at once |
| A review box, which step 4 sets from the reflection level | cavecrew: a `cavecrew-reviewer`. An edit box never goes to a `cavecrew-builder`: its prompt says it has no shell, makes a re-read its proof and ends unclear work on a question, so its report can never pass rule 3 of the lead |
| Before any heavy command (rule 2 of the lead) | resource-guard: its PreToolUse hook in Claude Code, `guard.py wait` by hand in any other tool |
| Every build, test run, install, typecheck, dev server, watcher and container | limited-run, with a memory cap: one-shot commands through the run's heavy lock, the rest stopped as soon as their result is in |
| Setting each worker's model and effort (the lead in the plan, a worker for its sub-workers) | claude-model-effort |
| The same, for a worker on a model that is not Claude | other-model-effort |
| A web page or its layout must be seen | browser-bidi: visual_test.py to look at a page, launch.py and bidi.py only to act on it |
| A failure followed by the fix that worked, or a step the next agent would have to work out again | a project skill in `.ia/skills/`, as Project skills says, never through writing-skills |
| The work is done and its checks pass | clean-code on the files this run changed; the same box runs the strip-ai-traces scan (step 6), so strip-ai-traces gets no worker of its own |
| Last | clean-commits, twice: the commit box before clean-code, then the closing box, which commits the rest and pushes |

## Procedure

One pass, in this order.

1. Read once every `<project>/.ia/skills/*/SKILL.md`: lessons from earlier runs on this project. In the
   plan, each box gets `lessons: <paths>` for the lessons whose `Use when` line names a command, file or
   error of that box, or `lessons: none`; the mapping and run kit workers get those naming a build or
   test command. A plan in `<project>/.ia/drive/` with boxes still unticked is resumed only when
   `/drive` came with no goal or the same goal (several such plans: the newest): write `lead: running`
   back on its first line, skip steps 2 to 4 (a plan without its run kit gets one first, as step 2
   says) and go to step 5, from its first unticked box. A plan whose first line already reads
   `lead: running` may be another session's live run: resume it only after one start question, a new
   plan (recommended) or the resume. Any other goal starts its own plan and leaves the old one as it is.
2. Send the mapping worker: a general-purpose agent at the minimum of claude-model-effort's
   Understanding an unknown codebase row, set on the call, with the block of `worker-brief.md` filled as
   its Mapping part says. That worker decides on graphify and scouts itself. Its report gives, under the
   Mapping headings, the files the goal touches, how to build and test, the graph path when graphify
   ran, the edge cases, a task count per completion level, the connected mechanics (candidates for the
   completion level), the branch and the uncommitted files.
   With that report in hand and before asking, the lead starts one run kit worker with
   `run_in_background: true` (in the foreground when the tool refuses), at the minimum of
   claude-model-effort's "Running tests, reading the failure, fixing" row, its block filled as the Run
   kit part of `worker-brief.md` says. It installs what is missing, runs the commands of clean-code's
   audit step 4 once each and the dev server until its ready line, and writes
   `<project>/.ia/drive/<YYYY-MM-DD>-<goal-slug>.run-kit.md`, named like the plan to come.
   That file is its proof. No box goes out before its report.
3. Ask, as rule 1 of Speaking says, then never again.
   For a new project (the goal asks for one, or `Branch:` says `no repository`), also ask its folder
   (the one the mapping worker named, recommended) and its commit language (English recommended, or
   French); `<project>` is that folder from then on. Its first box creates the folder when missing and
   runs `git init` there, and every commit box hands clean-commits the language as `--language en` or
   `--language fr`.
   When `Uncommitted:` lists files the goal touches, ask: work in a new worktree (recommended), or
   include those changes in this run's commits. A worktree is made by the first box through the
   using-git-worktrees skill; every later brief gives its path as `<project>`, and the plan stays where
   step 4 writes it.
   When `Branch:` is the default branch, also ask the branch: stay on it (recommended), or a new branch
   named after the goal in the repository's style, made by the first box. A worktree brings its own
   branch; on any other branch the run pushes the branch it is on.
   Each sign-in only a human can type that `Edges:` lists is asked too: sign in now (recommended), or
   the boxes that need it prove without it. Sign in now: a worker whose Box is that sign-in runs
   browser-bidi's `launch.py --port <p> --login --visible --url <page>` and pastes its output as proof,
   then one more question box asks the user to answer once signed in with the window closed. The answers
   keep `<p>`, and boxes that use it never share a `with:`.
4. Write the plan to `<project>/.ia/drive/<YYYY-MM-DD>-<goal-slug>.md` before any code: `lead: running`
   on its first line (the lead removes that line just before the run's last message, finished or
   stopped), then the goal, the answers to the questions and the mapping report's `Graph:` line at the
   top, with the reflection and completion levels on their own lines. The run tag is the goal slug cut
   to 24 characters. The completion level sets which connected mechanics become boxes. The reflection
   level sets where each box starts on its claude-model-effort row: *peu* the row's minimum, *moyen* one
   step above it, *beaucoup* two steps, *max* the row's ceiling, a custom level the nearest of these.
   Never past the ceiling, never the `max` effort level on Claude; claude-model-effort's rule 6 climbs
   from that start. The reflection level also adds the review boxes it calls for.
   Every task then becomes one `- [ ]` line, cut down to one change, with the test and on-screen or
   in-game proof the reflection level adds for it in the same box, its fields separated by ` | ` and its
   commands in backticks:

   ```text
   - [ ] b<n> | <action> | files: <paths> | check: `<command>` | proof: <`<command>` to run, seen: <what to look at>, or both> | row: <claude-model-effort row name up to its colon>, <model> <effort> | lessons: <paths, or none> | after: <ids, or none> | with: <ids, or none>
   ```

   `check:` holds the check that proves it done, `proof:` the proof that it works. `after:` names the
   boxes it waits for, `none` meaning every box above it; `with:` names the boxes it may run beside,
   `none` meaning it runs alone. Ids are never renumbered: a box added on the way takes the next free
   one. The brief's `Box:` field is this line, character for character. Ticking turns `- [ ] b<n> |`
   into `- [x] b<n> |`, and a box sent again at a new setting gets that setting written into its `row:`
   first.
   A box's check is the narrowest command that proves it: the test file or test id the box adds or
   touches, or the typecheck of its own package; the whole suite or a production build only when the
   box changes the build or test setup. A box with a test: its worker writes the test, pastes it
   failing, makes the change, pastes it passing, then looks. A proof box stands alone only when it
   covers several boxes (the whole feature seen running).
   Review boxes come from the reflection level only: none at *peu* and *moyen*, where each box's own
   proof is the check; at *beaucoup*, one `cavecrew-reviewer` box after the last code box, on every code
   box's files; at *max*, one after each code box, on its files. Its call sets the Code review row of
   claude-model-effort, above the agent file's `model: haiku`. It reads `git diff HEAD -- <files>`, and
   each new file whole, since that diff leaves new files out. Its proof is the
   `git diff --stat HEAD -- <files>` output and its finding lines, pasted; `No issues.` ticks it. Each
   bug or risk line becomes a new box, written in plain words, before it is handed out; a question line
   takes the safest reading.
   After the last code box and its review come the fixed boxes, in this order:
   - The full check box: the commands of clean-code's audit step 4, exactly as that step words them,
     each with its output written to `<project>/.ia/drive/<YYYY-MM-DD>-<goal-slug>.checks.txt`, next to
     the plan. A failure the run kit records as already failing is left and stays listed in that file.
     Any other failure is not sent back to that worker: the lead adds a fix box for it before the full
     check box, which goes out again after them.
   - The "done means" box: it proves the start answer on what done means, end to end, and is ticked
     only when that proof passes. It may go to the full check box's worker right after.
   - A commit box: clean-commits as a caller, its `files:` the union of every report's `files changed`,
     no push.
   - The clean-code box (step 6), then the closing box (step 7).

   Nothing to do lives outside this file.
5. Hand out the boxes in plan order, together when rule 2 of the lead allows it. Tick a box the moment
   its report shows its check and proof passing, never before. A failed check goes out again before any
   box waiting on it (its id in `after:`, or `after: none` below it); the others keep going. A task
   found on the way, in a report or otherwise, is added as a new box before it is handed out, but only
   when the goal cannot be done without it or it falls within the chosen completion level; anything else
   goes to a `## Seen, not done` list at the end of the plan file. A ticked box is never unticked: when
   a report shows its work broken, the repair is a new box. A box that failed only on a finding outside
   its files waits for that new box (`after:`), then goes out again at the same setting. Each report's
   `choices made` and `skipped` lines that are not `none` are copied under a `## Choices` heading at the
   end of the plan file, each after the box it came from. A report's `lesson written:` path is added to
   the lessons of every box not yet handed out whose command, file or error it names; a `deleted`
   path comes off every box. When a report
   changes a command, the lead edits the run kit before the next box goes out.
6. One worker runs clean-code on the files this run changed (its `files:`, the union of every report's
   `files changed`), its step commits allowed in caller mode, no push. Before measuring, it sets
   `"readers": 2` in `<project>/.ia/clean-code/config.json`, keeping any other key there, so
   clean-code's readers stay within two sub-workers. It runs
   `python -I ~/.claude/claude-skills/clean-code/scripts/measure.py <file> <file> ...` once, every
   changed file that still exists as an argument; only findings on those files become plan steps, the
   rest (repository-wide ones included) go under `Left as is` with "not changed by this run". When no
   box changed a file after the full check, the box names the checks file, and clean-code's audit step 4
   takes its results from that file (each failure a rule 12 finding with its output) instead of running
   the commands again. In this run, clean-code's verifier call sets the Code review row of
   claude-model-effort. clean-code may remove dead code inside the files this run changed, but never
   deletes a whole file this run did not create: that finding goes under `Left as is`, and the report's
   `skipped:` line names it. The clean-code box is one box: its steps live in clean-code's `plan.md`,
   and its `Left as is` items are never turned into boxes. The pass after the last step stops at
   `measure.py` on the same files, with no second verifier and no `score.py`, since the note is never
   said.
   Then it runs `python -I ~/.claude/claude-skills/strip-ai-traces/scripts/scan.py <file> --no-git --fix`
   once per changed file that still exists, in one shell call (clean-code rule 13), fixes every
   `by hand` row, and rereads the changed prose for rhythm, which no scan sees. The box passes when the
   last scan of every changed file shows `0 to fix by hand`; `flag` rows stay and are listed under
   findings. Its proof is that last `measure.py` output, the `plan ok` line of `plan_check.py` when a
   plan was written, the last full suite output (the last phase-end run, or the checks file when no
   phase applied a step) and each last scan's summary line, pasted. It runs on every change, however
   small: "checked by eye" or "too small to need it" is a skipped step.
   Where clean-code would send a subagent and the worker cannot, it does clean-code's Audit steps 1 to 5
   alone, reading every file itself, then stops and reports its run folder under findings; that is not
   a failed check. The lead then adds two boxes right after it: clean-code's verifier, prompted with
   `~/.claude/claude-skills/clean-code/verify-brief.md` in place of `worker-brief.md`, its proof the
   count line of `findings.py list` with no candidate left; then a fresh clean-code worker that goes on
   from Audit step 7 on that run folder, applies the plan and runs the scan above.
7. One closing worker runs clean-commits as a caller on this run's paths still uncommitted (its
   `files:`, the union of every report's `files changed`), writes the messages under strip-ai-traces'
   writing rules (`commit.py` and `push.py` check the rest), then pushes through `push.py`; no remote
   means the commits stay local. A path this run did not touch is left to its owner, without asking.
   After that, even when the push failed, it does the cleanup: it runs
   `python -I ~/.claude/claude-skills/limited-run/scripts/run.py list`, then `run.py stop <name>` for
   each listed name that is exactly `<run tag>-b<box number>-<n>` (never `stop --all`: those records are
   shared with every session on the PC). Then it stops each name, pid or Chrome port the reports list
   under `processes still running`, which the lead copies into its box line, and nothing else:
   `run.py stop <name or pid>`, or
   `python -I ~/.claude/claude-skills/browser-bidi/scripts/bidi.py close --port <port>` followed by
   browser-bidi's Procedure step 5 check for that port. Last, it tidies `<project>/.ia/skills/` as
   Project skills says. Its proof is the `push.py` output, a last `run.py list` and
   `ls <project>/.ia/skills` before and after the tidy, besides what rule 4 of the lead asks of a box
   that commits and one that cleans up.
   `100%` comes only once every box of the plan is ticked.

## Project skills

Any agent of the run, the lead, a worker or a sub-worker at any depth, may write a skill for this
project in `<project>/.ia/skills/<name>/SKILL.md`, with its scripts in `<name>/scripts/` when a script
does the job better than text. It must write one each time something fails and a later attempt works (a
command, a flag, a test, a wrong belief, a typo, or a box's failed `Earlier attempt`), before going on,
in the template of `worker-brief.md`, without loading writing-skills. It may write one at any other time a
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
