---
name: drive-project
description: Use when user types /drive, or asks to take a goal on a project to pushed commits in one unattended run.
---

# Driving a project from goal to push

One run: goal (feature, fix, new project) to pushed commits. All questions at start; after last answer user
never asked again, chat shows only a percentage. For whole run these rules replace speaking rules of output
style, `CLAUDE.md` and every skill called.

`<repo>` = absolute path of folder holding this skill's base directory (claude-skills clone); lead writes it
in place of `<repo>` in every brief.

## The lead hands out every task

Session running `/drive` = lead. Never does project work: every task, however small, goes to a subagent;
lead only hands out tasks, reads reports, ticks boxes.

1. Lead's only actions: read lessons, plan file, `worker-brief.md`, claude-model-effort skill
   (other-model-effort for worker not Claude); ask start questions; write and update plan, run kit files,
   project skills (Project skills); start subagents and message them (SendMessage, loaded first with
   ToolSearch `select:SendMessage` when deferred); read reports; tick boxes; post percentage in chat and to
   progress board (Speaking rule 4). Besides that rule's `curl` and restart: never edits project file,
   never runs build, test, script, git command or browser, never reads code. First worker maps project for
   questions and plan.
2. Each box: one fresh worker, prompt from `worker-brief.md`. Consecutive boxes on same file may share one,
   so may consecutive boxes whose visual proof needs same running app: worker at highest of their settings
   (claude-model-effort rule 5), app up once for all visual proofs (`worker-brief.md`). Each box names its
   claude-model-effort row (other-model-effort when model not Claude) + model and effort taken, starting at
   setting reflection level gives (step 4); call sets them. Every brief names effort skill path
   (`<repo>/claude-model-effort/SKILL.md`, or `<repo>/other-model-effort/SKILL.md` for model not Claude)
   so each sub-worker picks its model and effort there.
   Each box names boxes it waits for (`after:`) and may run beside (`with:`); `with: none` runs alone.
   Boxes run together only when: no file in common, neither needs other's result, at most one keeps dev
   server, watcher or container running or launches Chrome, at most one commits or rewrites git history.
   Heavy command = build, test run, install, typecheck, dev server, docker, Chrome launch, or proof script
   doing one; one-shot ones (build, test run, install, typecheck) take turns through run's heavy lock
   `<run tag>-heavy` (`worker-brief.md`). Max two workers working at once across whole tree; worker
   waiting on own sub-workers not counted. These rules replace CLAUDE.md rule keeping builds in main
   session: workers build and test themselves.
   Lead starts each worker with `run_in_background: true`, keeps both slots full: worker reports, tick or
   resend its box, then at once start first ready box in plan order (every `after:` box ticked) and, while
   another box still at work, one naming it in `with:` and named in its `with:`. Tool refuses background
   agent: foreground.
   Only Depth 1 worker with `with: none` may hand parts to sub-workers, two at once max; sub-worker never
   splits. Any other box too big for one worker returns `done: no` with one `split: <task>` line per part:
   not a failed check; lead writes parts as new boxes in its place. Agents a called skill starts
   (clean-code readers and verifier) count as sub-workers.
3. Box ticked only when report shows its check and proof passing, command and output pasted. Worker ran
   other check than box's: counts only when proving same behaviour (same test target, or wider run
   including it); lead writes command that ran into box's `check:` before ticking. Any other substitute,
   "close enough" included = no pasted check; `skipped:` line naming box's check or proof = failed check.
   Each worker's Agent call named after its box id (`b7`; several boxes: first one), so SendMessage
   reaches it after report. No pasted check, or failed one: one SendMessage to same worker asking command
   and output, or giving failing lines. Failed again or still nothing pasted: fresh worker one step up
   (claude-model-effort rule 6), `Earlier attempt:` = failed WORKER REPORT. Still failing at row's ceiling,
   or blocked on what no worker can fix (push rejected or refused, missing credential, refusal needing
   user): not sent again; lead writes failing lines under box in plan, one worker does step 7 cleanup
   without commit or push, run ends on last percentage + five words naming it.
   Not failed checks (out again at same setting, count toward neither claude-model-effort rule 6 nor
   ceiling): report failed only on file of its `Running beside:` line, or on heavy lock refusal: out again
   once boxes beside it reported, no lesson. Two boxes run together both fail: lower one in plan is such a
   report, out again only after other passes. `check: resource-guard timeout`: out again once no other box
   running; only third timeout in a row on one box ends run, like blocked box. Commit box refused by
   `checks.py` (`FAILED on these files`) or commit hook: not resent as is; lead first adds box fixing those
   files, then resends commit box.
4. Every box carries mandatory proof it works: every reflection level, *peu* included, every worker at
   every depth. Worker reads code and result it must change until it can say what it does (understand),
   runs check (test), looks at real outcome (see). Proof = script run, output pasted, + visual proof when
   result is page or screen (page seen through browser-bidi, screenshot looked at). Result nothing here can
   capture (desktop app, game outside browser): `script only` in `proof:`, script proof alone. What visual
   proof pastes: Rules of `worker-brief.md`. "It builds", "it looks right in the code", "should work" = no
   proof. Report pastes proof + one line of what was understood. Box without proof in plan not handed out;
   report without it = failed check. Worker that split box checks each sub-report's proof, adds own proof
   for whole.
5. "A subagent would cost more than doing it", "three small edits", "it is one line", "I already have the
   context", "just this once to save time": each = excuse this rule exists for. Box goes to worker at
   setting reflection level gives (step 4).

## Speaking

User hears from run three times: questions, percentages, last five words. Questions and last words in
user's language.

1. Questions only at start, `AskUserQuestion` boxes, as many as needed, recommended option first. Ask all
   that could change work: scope and what done means, stack when not set, every decision only user can
   make (public name or id, licence, URL user owns, money, anything deleted, anything published beyond
   push of run's branch). Read goal and mapping report first, so edge cases (input to handle, reading of
   vague word) asked here, not found later.
   Two boxes always asked, never skipped, options *peu*, *moyen*, *beaucoup*, *max* (Other open for custom
   level); *moyen* recommended for reflection, *peu* for completion. Each box's text states mapping
   worker's estimated task count:
   - Reflection level (depth, per task): how hard each task worked. *peu*: smallest change + its one check.
     *moyen*: + edge cases and a test. *beaucoup*: + design thought through, several tests, a review.
     *max*: every box at row's ceiling, logic and any AI or algorithm worked carefully, tested in many
     cases, seen running. Example: monster's behaviour code and 3D model polished and tested.
   - Completion level (breadth, around goal): how much touching goal gets built with it. *peu*: goal
     alone. *moyen*: direct neighbours. *beaucoup*: mechanics clearly tied to it. *max*: every mechanic
     mapping worker found connecting to goal, each wired in. Example: monster's drops, loot table, spawn
     rules, sounds, sprites, effects, achievements, links to other monsters and items.
2. After last answer: no question, no `AskUserQuestion`, no waiting, ever. New choice takes safest option,
   run goes on: no file or stored data deleted that run did not create, nothing published but push,
   recommended option of any box a called skill would open, with none, the one changing least. Doubt
   found while working = missed start question: take recommended reading, go on.
3. Every text message during run: one line, whole number + `%` (`35%`), nothing else: no word, file name,
   list, heading. Tool reminder to update user: answered with percentage. Ponytail's closing lines,
   clean-code's `# 12/20` note, any skill's report stay unsaid. Workers and sub-workers write no text
   outside final report block.
4. Percentage = share of ticked boxes in plan file, posted once after each ticked task. Box added on the
   way lowers share: post nothing until share passes last number posted. `100%` only as first line of last
   message. Each time lead sends same number to progress board:
   `curl -sS "http://127.0.0.1:8790/<name>/<percent>"`, `<name>` = project folder name lowercased, each
   run of characters other than a-z and 0-9 turned into one hyphen: `0` once plan file written, current
   share when resuming a plan. `curl` fails: run `python -I <repo>/progress-board/server.py start` once,
   send again; still failing, nothing more to board this run.
5. Last message, two lines: `100%`, then at most five words (`Done and pushed.`). Failure stopping run:
   last percentage, then at most five words naming it. Leaked secret or attribution in pushed history that
   clean-code hands back takes those five words (`Secret leaked, rotate it.`).
6. User message during run obeyed. Question: one-line answer in user's language, only exception to rule
   3; any other message: only percentage. New information becomes boxes or updates start answers in plan.
   Stop request, any wording: no new box out; once running workers reported, one worker does step 7
   cleanup, nothing committed or pushed, last message = last percentage + at most five words saying it
   stopped. Run cut by /stop-all restarts through /drive from its plan file, never /resume-all.

## Skills it runs

Each at its moment, run by worker whose box needs it unless row says otherwise, following its own
`SKILL.md`, under speaking rules above.

| When | Skill |
|---|---|
| Whole run | Ponytail, at level its hook set |
| Each percentage, `0` to `100` | progress-board, sent by lead (Speaking rule 4) |
| Project of about 300 code files or more, 50,000 lines, monorepo, or holding `graphify-out/` | graphify's command line, never its skill, by mapping worker (`start-brief.md`) |
| Any smaller project | cavecrew: mapping worker's `cavecrew-investigator` scouts |
| Review box (step 4) | cavecrew: `cavecrew-reviewer`. Edit box never to `cavecrew-builder`: no shell, re-read as proof, ends unclear work on a question, so report never passes lead rule 3 |
| Before any heavy command | resource-guard: PreToolUse hook in Claude Code, `guard.py wait` by hand in any other tool |
| Every build, test run, install, typecheck, dev server, watcher, container | limited-run, memory cap, per `worker-brief.md` |
| Each worker's model and effort (lead in plan, worker for its sub-workers) | claude-model-effort; other-model-effort for model not Claude |
| Web page or its layout must be seen | browser-bidi |
| Failure then fix that worked, or step next agent would work out again | project skill (Project skills), never through writing-skills |
| Work done, checks pass | clean-code on files run changed, same box runs strip-ai-traces scan (step 6) |
| Last | clean-commits twice: commit box before clean-code, closing box after (step 7) |

## Procedure

One pass, in order.

1. Read once every `<project>/.ia/skills/*/SKILL.md`: lessons of earlier runs. In plan each box gets
   `lessons: <paths>` for lessons whose `Use when` line names a command, file or error of that box, or
   `lessons: none`; mapping and run kit workers get those naming a build or test command. Plan in
   `<project>/.ia/drive/` with unticked boxes resumed only when `/drive` came with no goal or same goal
   (several: newest): write `lead: running` back on first line, skip steps 2 to 4 (plan without run kit
   gets one first, per step 2), go to step 5 from first unticked box. First line already `lead: running`:
   maybe another session's live run; resume only after one start question, new plan (recommended) or
   resume. Other goal: own plan, old one left as is.
2. Mapping worker: general-purpose agent at minimum of claude-model-effort's Understanding an unknown
   codebase row, set on call, `worker-brief.md` block filled per Mapping part of `start-brief.md`. It
   decides graphify and scouts itself. Report, under Mapping headings: files goal touches, build and test,
   graph path when graphify ran, edge cases, task count per completion level, connected mechanics
   (completion candidates), branch, uncommitted files.
   With that report, before asking, lead starts one run kit worker, `run_in_background: true` (foreground
   when refused), at minimum of claude-model-effort's "Running tests, reading the failure, fixing" row,
   block filled per Run kit part of `start-brief.md`. It installs what is missing, runs clean-code's audit
   step 4 commands once each and dev server until ready line, writes
   `<project>/.ia/drive/<YYYY-MM-DD>-<goal-slug>.run-kit.md`, named like plan to come. That file = proof.
   No box out before its report.
3. Ask per Speaking rule 1, then never again.
   New project (goal asks for one, or `Branch:` says `no repository`): also ask folder (mapping worker's,
   recommended) and commit language (English recommended, or French); `<project>` = that folder from then
   on. First box creates folder when missing, runs `git init` there; every commit box hands clean-commits
   `--language en` or `--language fr`.
   `Uncommitted:` lists files goal touches: ask new worktree (recommended) or include those changes in
   run's commits. Worktree made by first box through using-git-worktrees skill; later briefs give its
   path as `<project>`; plan stays where step 4 writes it.
   `Branch:` = default branch: also ask stay on it (recommended), or new branch named after goal in
   repository's style, made by first box. Worktree brings own branch; any other branch: run pushes it.
   Each sign-in only a human can type listed in `Edges:` asked too: sign in now (recommended), or boxes
   needing it prove without it. Sign in now: worker whose Box is that sign-in runs browser-bidi's
   `launch.py --port <p> --login --visible --url <page>`, pastes output as proof; one more question box
   asks user to answer once signed in, window closed. Answers keep `<p>`; boxes using it never share
   `with:`.
4. Write plan to `<project>/.ia/drive/<YYYY-MM-DD>-<goal-slug>.md` before any code: `lead: running` on
   first line (lead removes it just before last message, finished or stopped), then goal, answers,
   mapping report's `Graph:` line at top, reflection and completion levels on own lines. Goal slug = goal
   lowercased, accents dropped, each run of characters other than a-z and 0-9 turned into one hyphen, no
   hyphen at either end. Run tag = that slug cut to 19 characters, end hyphen dropped, then `-` and plan's
   start time as HHMM (24 characters max, so `<run tag>-heavy` stays within limited-run's 40), on own line
   in plan; resumed plan keeps it. Completion level sets which connected mechanics become boxes. Reflection
   level sets each box's start on its claude-model-effort row: *peu* minimum, *moyen* one step above,
   *beaucoup* two steps, *max* ceiling, custom level nearest of these. Never past ceiling, never `max`
   effort level on Claude; claude-model-effort rule 6 climbs from there. Reflection level also adds review
   boxes it calls for.
   Each task = one `- [ ]` line, cut to one change, with test and on-screen or in-game proof reflection
   level adds in same box, fields split by ` | `, commands in backticks:

   ```text
   - [ ] b<n> | <action> | files: <paths> | check: `<command>` | proof: <`<command>` to run, seen: <what to look at>, or both> | row: <claude-model-effort row name up to its colon>, <model> <effort> | lessons: <paths, or none> | after: <ids, or none> | with: <ids, or none>
   ```

   `check:` proves it done, `proof:` proves it works. `after:` boxes it waits for, `none` = every box above;
   `with:` boxes it may run beside, `none` = runs alone. Ids never renumbered: added box takes next free
   one. Brief's `Box:` = this line, character for character. Ticking turns `- [ ] b<n> |` into
   `- [x] b<n> |`; box resent at new setting gets it written into `row:` first.
   Check = narrowest command proving box: test file or test id it adds or touches, or typecheck of own
   package; whole suite or production build only when box changes build or test setup. Box with test:
   worker writes test, pastes it failing, makes change, pastes it passing, then looks. Proof box stands
   alone only when covering several boxes (whole feature seen running).
   Review boxes from reflection level only: none at *peu* and *moyen* (each box's own proof is the check);
   *beaucoup*: one `cavecrew-reviewer` box after last code box, on every code box's files; *max*: one after
   each code box, on its files. Call sets claude-model-effort's Code review row, above agent file's
   `model: haiku`. Reads `git diff HEAD -- <files>` + each new file whole (diff leaves new files out);
   proof = `git diff --stat HEAD -- <files>` output + finding lines. No commit yet
   (`git rev-parse -q --verify HEAD` fails): reads each file whole, proof = `git status --short -- <files>`
   output + finding lines. Finding lines, emoji dropped, one per line under `findings:` of its WORKER
   REPORT; `No issues.` there ticks it. Each bug or risk line becomes new box, plain words, before handed
   out; question line takes safest reading.
   After last code box and its review, fixed boxes, in order:
   - Full check box: clean-code's audit step 4 commands, exactly as worded there, each output written to
     `<project>/.ia/drive/<YYYY-MM-DD>-<goal-slug>.checks.txt` next to plan. Failure run kit records as
     already failing: left, stays listed there. Other failure not sent back to that worker: lead adds fix
     box before full check box, which goes out again after them.
   - "Done means" box: proves start answer on what done means, end to end; ticked only when that proof
     passes. May go to full check box's worker right after.
   - Commit box: clean-commits as caller, `files:` = union of every report's `files changed`,
     every path `commit.py` treats as tooling (`.ia/`, `.claude/`, `.cursor/`, `.aider*`, `CLAUDE.md`,
     `CLAUDE.local.md`, any depth) left out (`commit.py` refuses whole commit for one), no push.
   - Clean-code box (step 6), then closing box (step 7).
   - Their proofs: box that commits pastes `git log -1` and `git status -sb`, once pushed branch line shows
     no `ahead` or `push.py` printed `no remote: the commits stay local`; box that cleans up pastes
     `stopped <name> pid <n>` of each process stopped, browser-bidi's `browser closed, port <P> released`
     when a browser ran, then that skill's Procedure step 5 check, empty.

   Nothing to do lives outside this file.
5. Hand out boxes in plan order, together when lead rule 2 allows. Tick box the moment report shows check
   and proof passing, never before. Failed check out again before any box waiting on it (id in `after:`,
   or `after: none` below it); others keep going. Task found on the way (report or otherwise) added as new
   box before handed out, only when goal needs it or it falls within chosen completion level; else to
   `## Seen, not done` list at end of plan. Ticked box never unticked: work shown broken gets new repair
   box. Box failed only on finding outside its files waits for that box (`after:`), then out again at same
   setting. Each report's `choices made` and `skipped` lines not `none` copied under `## Choices` at end of
   plan, each after its box. Report's `lesson written:` path added to lessons of every box not yet handed
   out whose command, file or error it names; `deleted` path comes off every box. Report changes a
   command: lead edits run kit before next box.
6. One worker runs clean-code on files run changed (`files:` = commit box's list), step commits allowed in
   caller mode, no push. Before measuring, sets `"readers": 2` in `<project>/.ia/clean-code/config.json`,
   other keys kept, so clean-code readers stay within two sub-workers; last clean-code worker puts old
   value back (or removes key it added) before report. Runs
   `python -I <repo>/clean-code/scripts/measure.py <file> <file> ...` once, every changed file still
   existing as argument; only findings on those files become plan steps, rest (repository-wide included)
   under `Left as is` with "not changed by this run". No box changed a file after full check: box names
   checks file, clean-code's audit step 4 takes results from it (each failure a rule 12 finding with
   output) instead of rerunning. Here clean-code's verifier call sets claude-model-effort's Code review
   row. clean-code may remove dead code inside changed files, never deletes whole file run did not create:
   that finding under `Left as is`, named in `skipped:`. Clean-code box = one box: steps in clean-code's
   `plan.md`, `Left as is` items never boxes. Pass after last step stops at `measure.py` on same files, no
   second verifier, no `score.py`, since note never said.
   Then `python -I <repo>/strip-ai-traces/scripts/scan.py <file> --no-git --fix` once per changed file
   still existing, one shell call (clean-code rule 13), fixes every `by hand` row, rereads changed prose
   for rhythm, which no scan sees. Passes when last scan of every changed file shows `0 to fix by hand`;
   `flag` rows stay, listed under findings. Proof: last `measure.py` output, `plan ok` line of
   `plan_check.py` when a plan was written, last full suite output (last phase-end run, or checks file
   when no phase applied a step), each last scan's summary line, pasted. Runs on every change, even the
   smallest: "checked by eye" or "too small to need it" = skipped step.
   Clean-code would send a subagent and worker cannot: does clean-code's Audit steps 1 to 5 alone, reading
   every file itself, stops, reports run folder under findings; not a failed check. Lead adds two boxes
   right after: clean-code's verifier, prompted with `<repo>/clean-code/verify-brief.md` in place of
   `worker-brief.md`, proof = count line of `findings.py list` with no candidate left; then fresh
   clean-code worker going on from Audit step 7 on that run folder, applying plan, running scan above.
7. One closing worker runs clean-commits as caller on run's paths still uncommitted (`files:` = union of
   every report's `files changed`, every path `commit.py` treats as tooling (`.ia/`, `.claude/`,
   `.cursor/`, `.aider*`, `CLAUDE.md`, `CLAUDE.local.md`, any depth) left out), messages under
   strip-ai-traces' writing rules (`commit.py` and `push.py` check rest), pushes through `push.py`; no
   remote = commits stay local. Path run did not touch: left to owner, no asking.
   Then, even when push failed, cleanup: `python -I <repo>/limited-run/scripts/run.py list`, then
   `run.py stop <name>` for each listed name exactly `<run tag>-b<box number>-<n>` (never `stop --all`:
   records shared with every session on PC). Then stops each name, pid or Chrome port reports list under
   `processes still running` (lead copies them into its box line), nothing else: `run.py stop <name or pid>`,
   or `python -I <repo>/browser-bidi/scripts/bidi.py close --port <port>` + browser-bidi's Procedure step 5
   check for that port. Last, tidies `<project>/.ia/skills/` (Project skills). Proof: `push.py` output,
   last `run.py list`, `ls <project>/.ia/skills` before and after tidy, + step 4 proofs of a box that
   commits and one that cleans up.
   `100%` only once every plan box ticked.

## Project skills

Any agent of run (lead, worker, sub-worker at any depth) may write a project skill in
`<project>/.ia/skills/<name>/SKILL.md`, scripts in `<name>/scripts/`, per template and rules of
`worker-brief.md`; after a failure a later attempt got past, it must. This run, every project skill goes
there, in place of any folder user's instructions name.
Closing worker tidies folder each run: deletes each skill whose `Use when` line names file, script or
command project no longer has (checked with `ls` or `rg`), merges two covering same thing, lists each
under `lesson written:` (`deleted <path>` for one deleted).
`.ia/` and the other tooling paths are refused by `commit.py`, so no `files:` list carries them; project
skills stay on this machine, next run's step 1 reads them.
