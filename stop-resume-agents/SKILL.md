---
name: stop-resume-agents
description: Use when the user types /stop-all or /resume-all, asks to stop everything including subagents and record what each was doing, or asks to relaunch subagents from a resume.md left by an earlier stop.
---

# Stop all, resume all

/stop-all freezes the session and every subagent, collects a report from each, and writes resume.md
in the project's `.ia/` folder. /resume-all reads it and puts the unfinished agents back to work.
resume.md is the only memory that survives a closed session.

The files named below sit in this skill's base directory. Call the scripts with
`python -I "<base>/scripts/<name>.py"`, forward slashes, double quotes. On failure they print what to
do by hand. Scratch folder: `<temp>/claude-skills/stop-all` (`mkdir -p` before the first `--out`,
delete at the end). Both commands are orders: no opening questions beyond the ones in the steps.

## Rules

These hold for both commands, whatever the hurry.

1. Load the deferred tools first, in one call: `ToolSearch` with `select:SendMessage,TaskStop,CronList,CronDelete`,
   plus ListAgents, Agent or AskUserQuestion when missing. If one cannot load: without ListAgents the
   list is the digest plus your context; without SendMessage every agent counts as silent; without
   TaskStop write the running ones under `## Open questions` and tell the user; without
   CronList write the crons you remember as `to check`; without AskUserQuestion ask in plain text.
2. Write resume.md before waiting and update it after every answer: a session that dies mid-stop must
   still leave a usable file.
3. Every agent section holds its original prompt word for word in a fenced block.
4. Touch only what is yours: this session's subagents, the background tasks it started, and processes
   whose command line matches a command this session or its agents ran in the project folder. Peer
   sessions from ListAgents and the user's own editors, tools or Chrome: never.
5. No commit, push, stash or clean-up of project files during /stop-all. resume.md is never added to
   git. Only the scratch files get deleted.
6. Never open a raw transcript with cat, tail or Read (it can overflow the context). Use
   `agent_digest.py --out "<scratch>/<name>.md"`, `--agent <id>` included, and read that file.
7. Edit resume.md with Edit on a unique string, never by splitting on `## ` (quoted prompts hold
   headings). Pending fields read `pending <agent id>`.
8. Never delete a resume file. /stop-all never overwrites one, and never touches a resume.md whose first
   line is not `<!-- stop-resume-agents v1 -->`. /resume-all edits the file it resumes in place.

## /stop-all

In this order, none skipped.

1. Stop your own work. Finish only a half-written file; an irreversible operation already running
   (migration, deploy, push) reaches its safe point first.
2. Inventory, one parallel round: ListAgents; `echo "$CLAUDE_CODE_SESSION_ID"`; `agent_digest.py --list`;
   `resume_file.py find`; the background task ids you started; CronList; any /loop, workflow, server or
   Chrome port you opened; `git status`, `git diff --stat`, `git log -1` in each repo touched. An empty
   session id makes the digest refuse: rerun with `--latest` and check the ids match your agents.
   `NO_AGENT` is not an id. The agent list is ListAgents plus the digest (ListAgents forgets finished
   agents within minutes).
3. Earlier stop of this same session (newest `find` result with your session id, `State: STOPPED`): if
   nothing runs in ListAgents and no work happened since, answer "deja arrete" with its path and end.
   Otherwise carry on; agents with no activity since keep their old section (copy it in step 5, do not
   message them in step 6).
4. `agent_digest.py --out "<scratch>/digest.md"`, then read it.
5. Folder: `.ia/` at the repo root (`git rev-parse --show-toplevel`), else `.ia/` in the project folder,
   else `~/Desktop`. Never the home folder, Temp, a drive root, or the project root next to the code.
   Create `.ia/` if missing and keep it out of git through the exclude file, not `.gitignore`:

   ```bash
   git -C "<root>" check-ignore -q .ia/resume.md; [ $? -eq 1 ] && echo ".ia/" >> "$(git -C "<root>" rev-parse --path-format=absolute --git-common-dir)/info/exclude"
   ```

   An older stop's file at the project root stays there; /resume-all still finds it. A `resume.md`
   without the marker: write `resume-stop-all.md` instead. A marked file already there: rename it
   `resume-<mtime YYYY-MM-DD-HHMM>.md`; same session: set its state to `State: REPLACED by <new path>`;
   other session not resumed: keep its state and list it in the new file's `## Open questions`.
   Write the new file from `resume-template.md` with `State: STOP IN PROGRESS`, your own section, the repos,
   one section per depth 1 agent of the digest (depth 2 reports sit inside their parent's section). Then
   `resume_file.py log "<path>" stop`.
6. Send `report-request.md` unchanged, one SendMessage per agent, all in one turn, to every depth 1 agent,
   running or finished, except a finished one whose last words already are an AGENT REPORT. Message a
   depth 2 agent yourself only when its parent is finished. A failed send counts as silent.
7. Wait in rounds of `sleep 30` (foreground Bash): 10 rounds, or 2 per minute when /stop-all got a bare
   number as argument. Paste each AGENT REPORT into its section as its notification lands. Stop waiting
   once all answered. `ScheduleWakeup` only works inside /loop.
8. ListAgents again. For each agent still running: copy the `Pending at end` block of its
   `--agent <id>` digest into its section, TaskStop it, set `Reponse a l'arret : non, reconstruit depuis
   son journal`, and fill the section from the digest.
9. Processes outliving their agent: every `[background]` command in the digest and every server or
   watcher in a report. Find each by command line (`Get-CimInstance Win32_Process`); note matches with
   PID and command line, list the others as not found. A non-matching process is not yours.
10. Write every remaining item in resume.md in one edit, then stop them: background tasks and workflows
    with TaskStop, a dynamic /loop with `ScheduleWakeup({stop: true})`, crons this session created with
    CronDelete, servers by PID after reading their command line, Chrome ports with the chrome-bidi
    skill's close action (`bidi.ps1 -Action close`), step 9 processes with `taskkill /PID <pid> /T /F`
    through PowerShell.
11. Complete each main session findings entry by comparing report, digest and git; never trust a report alone. The digest
    sees Write and Edit only: shell-made changes show in `git status` and mtimes after the agent's first
    activity. State gaps plainly and flag untrustworthy results (tests run while another agent edited).
    Fill `To relaunch`, `Relaunch order`, owned files with `resume_file.py hash <files>`, questions, plan.
    Report Status maps to `Status:` as done, partial, not started,
    else unknown. Set `State: STOPPED`.
12. `resume_check.py "<path>" --agent <id>` for every depth 1 id until it prints OK, and ListAgents must
    show no running subagent. After three failed attempts write what is wrong under `## Open questions`
    and tell the user. Delete the scratch folder.
13. Answer in three or four lines in the user's language: what was stopped, the path, who did not answer. Then wait:
    nothing restarts before the user speaks.

## /resume-all

In order, from the file back to working agents.

1. Load the deferred tools as in rule 1. A path in the arguments wins. Otherwise `resume_file.py find`
   (looks in `.ia/` and at the root of the repo and of the current folder, then in the journals of
   every account; `REPLACED` files are skipped). Several files not resumed: AskUserQuestion, newest
   first. Only resumed ones: ask whether to resume the newest again. None: AskUserQuestion for the path.
   Never guess a file.
2. Read the whole file and run `resume_check.py` on it. `State: STOP IN PROGRESS` means the stop was cut:
   run the digest with `--session <id from the file>` and `--config <Claude account from the file>` and
   fill the gaps.
3. Reality check, one round: branch, HEAD, status and diff stat of each repo against the file;
   `resume_file.py hash` on every owned file against the recorded prints; ListAgents; free RAM, CPU, disk.
4. Drift is a moved HEAD, another branch, or an owned file whose print changed (unless the change is the
   agent's own recorded work). On drift, AskUserQuestion before relaunching the agents it touches; the
   others start meanwhile. An accepted drift goes into the brief as a known difference.
5. Depth 1 agents only, one by one (a parent's brief lists its children and their reports).
   `Status: done` or `To relaunch: no`: skip, write why. File written by this same session
   (origin session equals `$CLAUDE_CODE_SESSION_ID`): SendMessage the RESUME-ALL text of
   `relaunch-brief.md` to the old id and check as that file says. Otherwise, or if that fails: Agent in
   the background with the same subagent_type, model and effort, description `<old description> (resumed)`,
   prompt filled from `relaunch-brief.md`. Unknown model or effort (digest `default`, file `unknown`):
   leave the parameter out, never swap in another model. A type that no longer exists: general-purpose,
   same model.
6. Independent agents start together, four at most at once, the next when a slot frees. `after agent
   <id>` means after that agent finished and its result was checked. Two agents owning the same file
   never run together.
7. Relaunch the marked processes only when an agent or your own part needs them; close them at the end.
8. Right after the launches, edit resume.md: a `## Resumed on <date>` section above `## Log` (new
   session id, old id to new id or `SendMessage`, skipped agents and why, waiting agents, drift found),
   `State: RESUMED on <date>, session <id>`, a Log line, then `resume_file.py log "<path>" resume`.
   The file stays, marked RESUMED.
9. ListAgents must show every agent started now. Retry a failed launch once, then write it in resume.md
   and tell the user.
10. Delete the scratch folder, take back your own part from `## Main session`, answer in three or
    four lines in the user's language.
