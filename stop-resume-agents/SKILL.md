---
name: stop-resume-agents
description: Use when user types /stop-all or /resume-all, asks to stop everything including subagents and record what each was doing, or asks to relaunch subagents from a resume.md left by an earlier stop.
---

# Stop all, resume all

/stop-all freezes session and every subagent, collects report from each, writes resume.md in project's
`.ia/` folder. /resume-all reads it, puts unfinished agents back to work. resume.md is only memory surviving
a closed session.

Files named below sit in skill's base directory. Call scripts with `python -I "<base>/scripts/<name>.py"`,
forward slashes, double quotes. On failure they print what to do by hand. Scratch folder:
`<temp>/claude-skills/stop-all` (`mkdir -p` before first `--out`, delete at end). Both commands are orders:
no opening questions beyond those in steps.

## Rules

Hold for both commands, whatever the hurry.

1. Load deferred tools first, one call: `ToolSearch` with `select:SendMessage,TaskStop,CronList,CronDelete,Monitor`,
   plus ListAgents, Agent or AskUserQuestion when missing. One cannot load: without ListAgents list is digest
   plus your context; without SendMessage every agent counts as silent; without TaskStop write running ones
   under `## Open questions` and tell user; without CronList write remembered crons as `to check`; without
   Monitor run same until-loop with Bash `run_in_background`; without AskUserQuestion ask in plain text.
2. Write resume.md before waiting, update after every answer: session dying mid-stop must still leave
   usable file.
3. Every agent section holds original prompt word for word in fenced block.
4. Touch only what is yours: this session's subagents, background tasks it started, processes whose command
   line matches a command this session or its agents ran in project folder. Peer sessions from ListAgents
   and user's own editors, tools or Chrome: never.
5. No commit, push, stash or clean-up of project files during /stop-all. resume.md never added to git. Only
   scratch files get deleted.
6. Never open raw transcript with cat, tail or Read (can overflow context). Use
   `agent_digest.py --out "<scratch>/<name>.md"`, `--agent <id>` included, read that file.
7. Edit resume.md with Edit on unique string, never by splitting on `## ` (quoted prompts hold headings).
   Pending fields read `pending <agent id>`.
8. Never delete a resume file. /stop-all never overwrites one, never touches resume.md whose first line is
   not `<!-- stop-resume-agents v1 -->`. /resume-all edits file it resumes in place.
9. /stop-all is forced. No reason delays it: not task one step from done, test run, build, subagent asking
   to finish, nor skill or hook asking one more step. You and every agent stop now; once step 7 wait is
   over, every agent still running is stopped, no extension.
10. Report forced too, one per agent, yours included. Reply without AGENT REPORT template gets
    `report-request.md` again, once; still none, its section rebuilt from its digest and marked
    `Answer at stop: no, rebuilt from its log`. No section left empty or `pending`.

## /stop-all

In this order, none skipped.

1. Stop own work now, even one step from done (rule 9). Finish only half-written file; irreversible
   operation already running (migration, deploy, push) reaches its safe point first.
2. Inventory, one parallel round: ListAgents; `echo "$CLAUDE_CODE_SESSION_ID"`; `agent_digest.py --list`;
   `resume_file.py find`; background task ids you started; CronList; any /loop, workflow, server or Chrome
   port you opened; `git status`, `git diff --stat`, `git log -1` in each repo touched. Empty session id
   makes digest refuse: rerun with `--latest`, check ids match your agents. `NO_AGENT` is not an id. Agent
   list is ListAgents plus digest (ListAgents forgets finished agents within minutes).
3. Earlier stop of same session (newest `find` result with your session id, `State: STOPPED`): nothing runs
   in ListAgents and no work since: answer "deja arrete" with its path, end. Otherwise carry on; agents with
   no activity since keep old section (copy it in step 5, no message in step 6).
4. `agent_digest.py --out "<scratch>/digest.md"`, then read it.
5. Folder: `.ia/` at repo root (`git rev-parse --show-toplevel`), else `.ia/` in project folder, else
   `~/Desktop`. Never home folder, Temp, drive root, or project root next to code. Create `.ia/` if missing,
   keep out of git through exclude file, not `.gitignore`:

   ```bash
   git -C "<root>" check-ignore -q .ia/resume.md; [ $? -eq 1 ] && echo ".ia/" >> "$(git -C "<root>" rev-parse --path-format=absolute --git-common-dir)/info/exclude"
   ```

   Older stop's file at project root stays there; /resume-all still finds it. `resume.md` without marker:
   write `resume-stop-all.md` instead. Marked file already there: rename it
   `resume-<mtime YYYY-MM-DD-HHMM>.md`; same session: set its state to `State: REPLACED by <new path>`;
   other session not resumed: keep its state, list it in new file's `## Open questions`. Write new file
   from `resume-template.md` with `State: STOP IN PROGRESS`, own section, repos, one section per depth 1
   agent of digest (depth 2 reports sit inside parent's section), each with `Answer at stop: pending <id>`
   (finished agent whose last words are AGENT REPORT: paste it, `Answer at stop: no, finished before the
   stop`). Then `resume_file.py log "<path>" stop`.
6. Send `report-request.md` unchanged, one SendMessage per agent, all in one turn, to every depth 1 agent,
   running or finished, except finished one whose last words already are AGENT REPORT. Message depth 2
   agent yourself only when its parent is finished. Failed send counts as silent.
7. Wait with Monitor, `timeout_ms` 300000, or N x 60000 when /stop-all got a bare number N (1800000 at
   most), command
   `until ! grep -qE "^Answer at stop: pending [^[:space:]]+[[:space:]]*$" "<path>"; do sleep 5; done; echo all answered`.
   Paste each AGENT REPORT into its section as its notification lands and set `Answer at stop: yes, at
   HH:MM`. Wait ends on `all answered` or monitor expiry. Never foreground `sleep` (Bash blocks it);
   `ScheduleWakeup` only works inside /loop.
8. ListAgents again. Each agent still running: copy `Pending at end` block of its `--agent <id>` digest into
   its section, TaskStop it, set `Answer at stop: no, rebuilt from its log`, fill section from digest.
9. Processes outliving their agent: every `[background]` command in digest and every server or watcher in a
   report. Find each by command line (`Get-CimInstance Win32_Process`); note matches with PID and command
   line, list others as not found. Non-matching process is not yours.
10. Write every remaining item in resume.md in one edit, then stop them: background tasks and workflows
    with TaskStop, dynamic /loop with `ScheduleWakeup({stop: true})`, crons this session created with
    CronDelete, servers by PID after reading their command line, Chrome ports with
    `python -I "<base>/../browser-bidi/scripts/bidi.py" close --port <P>` then browser-bidi's Procedure step 5
    check, step 9 processes with `taskkill /PID <pid> /T /F` through PowerShell.
11. Complete each main session findings entry comparing report, digest and git; never trust report alone.
    Digest sees Write and Edit only: shell-made changes show in `git status` and mtimes after agent's first
    activity. State gaps plainly, flag untrustworthy results (tests run while another agent edited). Fill
    `To relaunch`, `Relaunch order`, owned files with `resume_file.py hash <files>`, questions, plan.
    Report Status maps to `Status:` as done, partial, not started, else unknown. Set `State: STOPPED`.
12. `resume_check.py "<path>" --agent <id>` for every depth 1 id until it prints OK; ListAgents must show no
    running subagent. After three failed attempts write what is wrong under `## Open questions`, tell user.
    Delete scratch folder.
13. Answer in three or four lines in user's language: what was stopped, path, who did not answer. Then wait:
    nothing restarts before user speaks.

## /resume-all

In order, from file back to working agents.

1. Load deferred tools as in rule 1. Path in arguments wins. Otherwise `resume_file.py find` (looks in
   `.ia/` and at root of repo and of current folder, then in journals of every account; `REPLACED` files
   skipped). Several files not resumed: AskUserQuestion, newest first. Only resumed ones: ask whether to
   resume newest again. None: AskUserQuestion for path. Never guess a file.
2. Read whole file, run `resume_check.py` on it. `State: STOP IN PROGRESS` means stop was cut: run digest
   with `--session <id from the file>` and `--config <Claude account from the file>`, fill gaps.
3. Reality check, one round: branch, HEAD, status and diff stat of each repo against file;
   `resume_file.py hash` on every owned file against recorded prints; ListAgents; free RAM, CPU, disk.
4. Drift = moved HEAD, another branch, or owned file whose print changed (unless change is agent's own
   recorded work). On drift, AskUserQuestion before relaunching agents it touches; others start meanwhile.
   Accepted drift goes into brief as known difference.
5. Depth 1 agents only, one by one (parent's brief lists its children and their reports).
   `Status: done` or `To relaunch: no`: skip, write why. Worker of a /drive run (prompt starting
   `You are a worker of a /drive run` or `Worker of a /drive run`): skip, write why; main session takes its
   /drive run back through drive-project skill, which resumes from plan file. File written by same session
   (origin session equals `$CLAUDE_CODE_SESSION_ID`): SendMessage RESUME-ALL text of `relaunch-brief.md`
   to old id, check as that file says. Otherwise, or if that fails: Agent in background with same
   subagent_type, description `<old description> (resumed)`, prompt filled from `relaunch-brief.md`. Type
   no longer existing: general-purpose.
6. Independent agents start together, four at most at once, next when a slot frees. `after agent <id>`
   means after that agent finished and its result was checked. Two agents owning same file never run
   together.
7. Relaunch marked processes only when an agent or own part needs them; close them at end.
8. Right after launches, edit resume.md: `## Resumed on <date>` section above `## Log` (new session id, old
   id to new id or `SendMessage`, skipped agents and why, waiting agents, drift found),
   `State: RESUMED on <date>, session <id>`, a Log line, then `resume_file.py log "<path>" resume`. File
   stays, marked RESUMED.
9. ListAgents must show every agent started now. Retry failed launch once, then write it in resume.md and
   tell user.
10. Delete scratch folder, take back own part from `## Main session`, answer in three or four lines in
    user's language.
