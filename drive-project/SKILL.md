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

Speed comes from four things, never traded away: chains run side by side, one worker per chain, proofs at
the right size, no waiting on nothing.

## The lead hands out every task

Session running `/drive` = lead. Never does project work: reads goal, reports and plan; asks start
questions; writes and ticks plan; starts workers and messages them (SendMessage, loaded first with ToolSearch
`select:SendMessage` when deferred); posts percentage. Never edits project file, never runs build, test,
script, git command or browser, never reads code. "Only one line", "I already have the context", "a worker
costs more" = excuses this rule exists for.

1. Plan = chains. Chain = boxes on same feature or same files, done in order by one worker. Chains sharing no
   file and needing no result from each other run at same time: lead starts them in one message, one Agent
   call each, `run_in_background: true` (foreground only when refused). No cap: resource-guard holds heavy
   commands when PC is short.
2. Each chain's Agent call named after chain id (`c2`), so SendMessage reaches it after report. Worker gets
   `worker-brief.md` block, model and effort set on call from chain's `row:`.
3. Chain ticked box by box from its report: box ticked only when report pastes its check and proof passing.
   Worker ran other check proving same behaviour (same test target, or wider run including it): lead writes
   command that ran into box's `check:` before ticking. Any other substitute, or `skipped:` naming box's check
   or proof = failed box.
4. Failed box, or nothing pasted: one SendMessage to same worker with failing lines (`Fix b7. Check failed.
   Paste command + output.`). Fails again: fresh worker one step up (claude-model-effort rule 6) on chain's
   unticked boxes, `Earlier attempt:` = failed WORKER REPORT. Failing at row's ceiling, or blocked on what no
   worker can fix (push refused, missing credential, refusal needing user): run ends per Speaking rule 5,
   after closing worker cleans up without commit or push.
5. Not failed (resent at same setting, no step up): failure only on file of a chain running beside
   (`neighbour:`), heavy lock refusal, `check: resource-guard timeout` (resent once nothing runs beside it;
   third in a row ends run like blocked box). Commit refused by `checks.py` or a hook: lead adds fix box
   first, then resends.
6. Report with `split:` lines: not failed; each line becomes new chain or box in its place.
7. Text lead sends to a worker = strict minimum per terse-speech, Agent to agent. Block of `worker-brief.md`
   stays as is, nothing added around it. Code, commands, paths, error text quoted exact.

## Speaking

User hears from run three times: questions, percentages, last five words. Questions and last words in
user's language.

1. Questions only at start, `AskUserQuestion` boxes, as many as needed, recommended option first: scope and
   what done means, stack when not set, every decision only user can make (public name or id, licence, URL
   user owns, money, anything deleted, anything published beyond push of run's branch), edge cases mapping
   found. Two boxes always asked, options *peu*, *moyen*, *beaucoup*, *max* (Other open), each stating mapping
   worker's task count; *moyen* recommended for reflection, *peu* for completion:
   - Reflection (depth per task). *peu*: smallest change + its check. *moyen*: + edge cases and a test.
     *beaucoup*: + design thought through, several tests, one review of whole run. *max*: + review per chain,
     logic and any AI or algorithm tested in many cases, seen running.
   - Completion (breadth around goal). *peu*: goal alone. *moyen*: direct neighbours. *beaucoup*: mechanics
     clearly tied to it. *max*: every connected mechanic mapping found, each wired in.
2. After last answer: no question, no waiting, ever. New choice takes safest option: nothing deleted run did
   not create, nothing published but push, a called skill's recommended option, else the one changing least.
3. Every text message during run: one line, whole number + `%`, nothing else. Workers write no text outside
   final report block. Any skill's closing line, note or report stays unsaid.
4. Percentage = share of ticked boxes, posted after each report that ticks one; never lower than last posted.
   Same number to board: `curl -sS "http://127.0.0.1:8790/<name>/<percent>"`, `<name>` = project folder
   name lowercased, each run of characters other than a-z and 0-9 one hyphen; `0` once plan written. `curl`
   fails: `python -I <repo>/progress-board/server.py start` once, send again; still failing, board dropped.
5. Last message, two lines: `100%` (or last percentage when run failed or stopped), then at most five words
   (`Done and pushed.`, `Secret leaked, rotate it.`).
6. User message during run obeyed. Question: one-line answer, only exception to rule 3. New information
   becomes boxes or updates answers in plan. Stop request: no new chain out; once running workers reported,
   closing worker cleans up, nothing committed or pushed. Run cut by /stop-all restarts through /drive from
   its plan, never /resume-all.

## Skills it runs

| When | Skill |
|---|---|
| Whole run | terse-speech, least-code, loaded by their hooks |
| Each percentage | progress-board, lead only |
| Finding code, project over 50 code files | code-map, built by mapping worker, used through `Graph:` |
| Each worker's model and effort | claude-model-effort; other-model-effort for model not Claude |
| Heavy command | resource-guard hook; limited-run for build, test, install, server, container |
| Page or layout seen | browser-bidi |
| Failure then fix that worked | project skill (Project skills) |
| End of work | clean-code + strip-ai-traces scan (clean box), clean-commits (clean and closing boxes) |
| Goal about speed, size or memory, or reflection *max* | `<repo>/drive-project/optimise-brief.md` (optimise box) |

## Procedure

One pass, in order.

1. Plan in `<project>/.ia/drive/` with unticked boxes resumed when `/drive` came with no goal or same goal
   (several: newest): first line back to `lead: running`, skip to step 5 from first unticked box. First line
   already `lead: running`: maybe another session's live run; one start question, new plan (recommended) or
   resume. Other goal: own plan, old one left as is.
2. Mapping worker, block per Mapping part of `start-brief.md`, at minimum of claude-model-effort's
   Understanding an unknown codebase row. With its report, before asking, run kit worker starts in
   background, block per Run kit part, at minimum of "Running tests, reading the failure, fixing" row. No
   chain out before run kit report.
3. Ask per Speaking rule 1, then never again. Also asked, when they apply:
   - optimise box will run: technologies to use or avoid (recommended `none given, AI picks`); graphics card
     (recommended `use it only when measured gain`, or `never`).
   - New project (goal asks one, or `Branch:` says `no repository`): folder (mapping's, recommended) and
     commit language (English recommended, or French). First box creates folder, runs `git init`.
   - `Uncommitted:` lists goal's files: new worktree (recommended, first box makes it through
     using-git-worktrees, later briefs give its path as `<project>`) or include those changes.
   - `Branch:` = default branch: stay (recommended) or new branch named after goal, made by first box.
   - Each sign-in only a human can type (`Edges:`): sign in now (recommended) or prove without it. Sign in
     now: a worker runs browser-bidi's `launch.py --port <p> --login --visible --url <page>`, one more
     question box asks user to answer once signed in. Chains using port `<p>` never run beside each other.
4. Write plan `<project>/.ia/drive/<YYYY-MM-DD>-<goal-slug>.md` before any code. Slug = goal lowercased,
   accents dropped, each run of characters other than a-z and 0-9 one hyphen, none at either end. Top lines:
   `lead: running`, goal, `Run tag: <slug cut to 19, end hyphen dropped>-<HHMM start>`, `Run kit: <path>`,
   `Graph:`, reflection and completion levels, answers (one line each). Then chains:

   ```text
   ## c<n> <feature> | row: <claude-model-effort task name, cut at its first colon>, <model> <effort> | lessons: <paths, or none> | after: <chain ids, or none> | proof: <`command`, seen: <what>, or script only>
   - [ ] b<n> | <action> | files: <paths> | check: `<command>`
   ```

   `after:` = chains whose result this one needs; `none` = starts at once. Never implied by order. Chains
   with `after: none` and no shared file start together. Ids never renumbered; added ones take next free id.
   Ticking turns `- [ ] b<n> |` into `- [x] b<n> |`, one `sed` per report for all its boxes. `<repo>`,
   `<plan>` and every path written resolved, never as a placeholder.
   - Row = the work the chain does (code chain: Everyday code, Large feature, or closer row), not its check.
   - Boxes: one change each. `check:` = narrowest command proving it (test it adds or touches, typecheck of
     own package; CSS or markup only: the chain's page proof); whole suite or production build only when box
     changes build or test setup.
   - Chain `proof:` = proof whole chain works, taken once after its last box: script run, plus page seen
     when result is a page (`seen:`). Visual proof, container rebuild and app start happen there, never per
     box. Result nothing here can capture: `script only`.
   - Starting setting from reflection: *peu* and *moyen* row minimum, *beaucoup* one step above, *max* two
     steps, never past ceiling, never `max` effort on Claude. Climbs only per lead rule 4.
   - `lessons:` = project skills whose `Use when` names a command, file or error of chain; picked from
     mapping report's `Lessons:` line, never by reading every skill.
   - Review chain: *beaucoup* one after last code chain on all code files; *max* one after each code chain.
     Row Code review. Reads `git diff HEAD -- <files>` + new files whole (no commit yet: files whole);
     proof = `git diff --stat HEAD -- <files>` (or `git status --short -- <files>`) + finding lines, `No
     issues.` when none. Each bug or risk line becomes a box before going on.
   - Fixed end chains, in order, each `after:` every code and review chain, one box each, `files: none`
     (`clean` and `close` get theirs from reports when they go out), `check:` = the proof they name:
     - `final`: clean-code's audit step 4 commands as worded there, outputs to `<plan>.checks.txt`
       (failure run kit lists as already failing stays), then proof of start answer on what done means, end
       to end. Row Running tests at minimum. New failure: fix box added to the chain that owns the file,
       `final` resent after.
     - `optimise`, only when Skills table says so, row Performance and profiling: optimise-brief.md on
       run's files; before and after measures pasted.
     - `clean`: step 6.
     - `close`: step 7, row Run upkeep.
   Nothing to do lives outside this file.
5. Start every ready chain (all `after:` chains ticked, no shared file with a running one). Report in: tick,
   copy `choices made` and `skipped` lines not `none` under `## Choices` after chain, then start every chain
   that became ready. Task found on the way: new box in owning chain (or new chain) only when goal needs it or
   completion level covers it; else under `## Seen, not done`. Ticked box never unticked: repair = new box.
   `lesson written:` path joins `lessons:` of chains not yet out that it names; `deleted` path comes off.
   Report changes a command: lead edits run kit before next chain.
6. `clean` worker, row Rewriting for readability, structure or speed, minimum. `files:` = union of every
   report's `files changed`, tooling paths left out (`.ia/`, `.claude/`, `.cursor/`, `.aider*`,
   `CLAUDE.md`, `CLAUDE.local.md`, any depth). In order:
   1. clean-commits as caller on `files:`, no push: run's work committed before tidying.
   2. clean-code on `files:`, step commits allowed in caller mode, no push. Sets `"readers": 2` in
      `<project>/.ia/clean-code/config.json` (other keys kept, old value put back before report). Runs
      `python -I <repo>/clean-code/scripts/measure.py <file> ...` once on files still existing; only findings
      on those files become steps, rest under `Left as is`. Audit step 4 results come from `<plan>.checks.txt`
      when no box changed a file after `final`. Verifier only at reflection *beaucoup* and *max*, row Code
      review; else worker checks each finding itself. Never deletes a whole file run did not create. After
      last step: `measure.py` on same files once, no second verifier, no `score.py`.
   3. `python -I <repo>/strip-ai-traces/scripts/scan.py <file> --no-git --fix` per file still existing, one
      shell call; fixes every `by hand` row; passes at `0 to fix by hand`.
   Proof: last `measure.py` output, `plan ok` line when a plan was written, last suite output, each scan
   summary line, `git log --oneline -3`. Clean-code would send a subagent and worker cannot: Audit steps 1 to
   5 alone, run folder under findings, not a failed check; lead adds verifier box (prompt
   `<repo>/clean-code/verify-brief.md`) then a fresh clean worker going on from Audit step 7.
7. `close` worker: clean-commits as caller on run's paths still uncommitted (tooling paths left out),
   pushes through `push.py`; no remote = commits stay local. Then, even when push failed:
   `python -I <repo>/limited-run/scripts/run.py list`, `run.py stop <name>` for each name starting
   `<run tag>-` (never `stop --all`), each item reports listed under `processes still running`, browser-bidi
   `bidi.py close --port <port>` + its Procedure step 5 check per port. Then tidies `<project>/.ia/skills/`
   (Project skills). Proof: `push.py` output, `git status -sb` without `ahead` (or `no remote: the commits
   stay local`), last `run.py list`, `stopped ...` and `browser closed ...` lines, `ls <project>/.ia/skills`
   before and after. `100%` only once every box ticked; lead removes `lead: running` just before last message.

## Project skills

Any worker may write `<project>/.ia/skills/<name>/SKILL.md` (scripts in `<name>/scripts/`) per template of
`worker-brief.md`; after a failure a later attempt got past, it must. Bug of a claude-skills script (bidi,
clean-code, limited-run, ...) is no project skill: under findings, path and failing lines. Closing worker
deletes each skill whose `Use when` names file, script or command project no longer has, merges two covering
same thing, lists each under `lesson written:`. `.ia/` is never committed; next run's mapping lists it.
