---
name: stop-resume-agents
description: Use when the user types /stop-all or /resume-all, asks to stop everything including the subagents and record what each one was doing, where and in which files, or asks to relaunch the subagents from a resume.md left by an earlier stop.
---

# Stop all, resume all

## Overview

Once per session, before following this skill, run
`python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"` and read the line it prints.
When that file does not exist, go on without it. After a line that starts with `updated`, read this file
again before going on.

/stop-all freezes the session and every subagent, collects a report from each one, and writes
resume.md in the project's `.ia/` folder. /resume-all reads that file and puts every unfinished
agent back to work. resume.md is the only memory that survives a closed session: what it does not
hold is lost.

File names below sit in this skill's base directory (shown when the skill loads, otherwise
`$CLAUDE_CONFIG_DIR/skills/stop-resume-agents`, or `~/.claude/skills/stop-resume-agents` when the
variable is empty). Call the scripts by absolute path with `python -I`, the path written with
forward slashes inside double quotes: `python -I "C:/Users/.../scripts/agent_digest.py"`. They
never crash: on failure they print what to do by hand. The scratch folder is
`<temp>/claude-skills/stop-all`, for both commands (`<temp>` is the system temp folder,
`tempfile.gettempdir()`): create it with `mkdir -p` before the first `--out`, delete it at the end.

Both commands are orders: they skip the usual opening questions. The only questions allowed are
the ones written in the steps below.

## Rules that never bend

These hold for both commands, whatever the hurry.

1. Load the deferred tools first, in one call: `ToolSearch` with
   `select:SendMessage,TaskStop,CronList,CronDelete`, adding ListAgents, Agent or AskUserQuestion
   when they are missing from your tools. A tool that still cannot load: without ListAgents the
   list is the digest plus your context; without SendMessage every agent counts as silent (step 8);
   without TaskStop write the running ones under `## Questions sans reponse` and tell the user;
   without CronList write the crons you remember as `a verifier`; without AskUserQuestion ask in
   plain text and wait for the answer. When the inventory shows an MCP instance you opened (a game
   editor, a 3D tool, a sound editor), load its save and close tools in the same way.
2. Write resume.md before waiting, then update it after every answer. A session that dies in the
   middle of the stop must still leave a usable file.
3. Every agent section carries its original prompt word for word, from the digest or from your own
   context, in a fenced block.
4. Touch only what is yours: this session's subagents (the digest reads this session only), the
   background tasks this session started, and processes whose command line matches a command this
   session or its agents ran in the project folder. Peer sessions shown by ListAgents and the
   user's own editors, 3D tools, sound editors or Chrome: never.
5. No commit, no push, no stash, no clean-up of project files during /stop-all. resume.md is never
   added to git. Only this skill's scratch files get deleted.
6. Never open a raw transcript with cat, tail or Read: one file can overflow the context. Use
   `scripts/agent_digest.py --out "<scratch>/<name>.md"`, `--agent <id>` included, and read that file.
7. Edit resume.md with Edit on a unique string, never by splitting it on `## `: quoted prompts
   and reports contain headings of their own. Pending fields read `en attente <agent id>`.
8. Never delete a resume file. /stop-all never overwrites one and never touches a resume.md whose
   first line is not `<!-- stop-resume-agents v1 -->`: that one belongs to the user. /resume-all
   edits the file it resumes, in place.

## /stop-all

The steps run in this order, and none is skipped.

1. Stop your own work at once. Finish only a half-written file. An irreversible operation already
   running (migration, deploy, push) reaches its safe point first.
2. Inventory, in one parallel round: ListAgents; `echo "$CLAUDE_CODE_SESSION_ID"`; `agent_digest.py
   --list`; `resume_file.py find`; the background task ids you started (in your context); CronList;
   any /loop, workflow, server, MCP instance or Chrome port you opened; `git status`, `git diff
   --stat` and `git log -1` in each repo you touched. An empty session id makes the digest refuse:
   rerun it with `--latest` and check that the ids it prints match your agents. `NO_AGENT` means no
   transcript, it is not an id. The agent list is the union of ListAgents and the digest: ListAgents
   forgets finished agents within minutes.
3. Earlier stop of this same session (newest file from `find` with your session id, `Etat :
   ARRETE`): nothing running in ListAgents and no work since its stop time means answer "deja
   arrete" with its path, and end. Otherwise carry on, and agents with no activity since that stop
   keep their old section: copy it in step 5 and do not message them in step 6.
4. Run `agent_digest.py --out "<scratch>/digest.md"` and read it.
5. Pick the folder: `.ia/` at the root of the repo you worked in (`git rev-parse --show-toplevel`),
   else `.ia/` in the project folder you worked in, else `~/Desktop` itself. Never the home folder
   itself, Temp or a drive root, and never the project root next to the code. Create `.ia/` when
   missing; in a repo, keep it out of git through the exclude file, which leaves `.gitignore` alone:

   ```bash
   git -C "<root>" check-ignore -q .ia/resume.md; [ $? -eq 1 ] && echo ".ia/" >> "$(git -C "<root>" rev-parse --path-format=absolute --git-common-dir)/info/exclude"
   ```

   A resume file an older stop left at the project root stays there: /resume-all still finds it, and
   nothing moves it. A `resume.md` in the folder without the marker: write `resume-stop-all.md`
   instead. A marked file already there: rename it `resume-<its mtime as AAAA-MM-JJ-HHMM>.md`; same
   session, set its state to `Etat : REMPLACE par <new path>`; other session not resumed, keep its
   state and add it to the new file's `## Questions sans reponse`. Write the new file from
   `resume-template.md` with `Etat : ARRET EN COURS`, your own section, the repos, one section per
   agent of depth 1 from the digest. Depth 2 agents get no section: their report sits inside their
   parent's. Then `resume_file.py log "<path>" stop`.
6. Send the text of `report-request.md`, one SendMessage per agent, all in the same turn, to every
   depth 1 agent of the list, running or finished, except a finished one whose last words already
   are an AGENT REPORT. Depth 2 agents get it from their parent; message one yourself only when its
   parent is finished. A failed send: that agent counts as silent.
7. Wait in rounds of `sleep 30` (foreground Bash): 10 rounds (5 minutes), or 2 rounds per minute
   when /stop-all received a bare number as argument. Notifications arrive with the tool results:
   paste each AGENT REPORT into its section as it lands. Stop waiting once every agent has answered.
   `ScheduleWakeup` is no help here, it only works inside /loop.
8. Then ListAgents. For each agent still running: copy the `Pending at end` block of its
   `--agent <id>` digest into its section, TaskStop it, set `Reponse a l'arret : non, reconstruit
   depuis son journal`, and fill the section from the digest.
9. Processes outliving their agent: every `[background]` command in the digest, of any agent, and
   every server or watcher in a report. Find each by command line (`Get-CimInstance Win32_Process`)
   and note those that match with PID and command line; the others are listed as not found. A process
   whose command line does not match one you ran is not yours.
10. Write every remaining item in resume.md in one edit, then stop them: background tasks with
    TaskStop, a dynamic /loop with `ScheduleWakeup({stop: true})`, crons this session created with
    CronDelete, workflows with TaskStop, servers by PID after reading their command line, MCP
    instances saved with their save tool then closed, Chrome ports with the chrome-bidi skill's close action
    (`bidi.ps1 -Action close`), processes from step 9 with `taskkill /PID <pid> /T /F` run through PowerShell.
11. Complete each `Constat`: compare the report with the digest and git, never trust a report alone.
    The digest sees Write and Edit only: files changed through the shell show up in `git status` and
    in mtimes after the agent's first activity. Write any gap plainly, flag results that cannot be
    trusted (tests run while another agent was editing). Fill `A relancer`, `Ordre de relance`, owned
    files with the output of `resume_file.py hash <files>`, questions and plan. The report's Status
    maps to `Statut :` as done to termine, partial to partiel, not started to pas commence, anything
    else to inconnu. Set `Etat : ARRETE`.
12. Check: `resume_check.py "<path>" --agent <id>` for every depth 1 id until it prints OK, and
    ListAgents must show no running subagent. Three failed attempts: write what is still wrong
    under `## Questions sans reponse` and tell the user. Delete the scratch folder.
13. Answer in three or four French lines: what was stopped, the path, who did not answer. Then wait:
    nothing restarts before the user speaks.

## /resume-all

The resume runs in order too, from the file back to working agents.

1. Load the deferred tools as in rule 1. A path given in the arguments wins. Otherwise run
   `resume_file.py find`: it looks in `.ia/` and at the root of the repo and of the current folder,
   then reads the journals of every account. `REMPLACE` files are skipped.
   Several files not resumed: AskUserQuestion, newest first. Only resumed ones: ask whether to
   resume the newest again. None: AskUserQuestion for the path. Never guess a file.
2. Read the whole file, run `resume_check.py` on it. `Etat : ARRET EN COURS` means the stop was cut:
   run the digest with `--session <id from the file>` and `--config <Compte Claude from the file>`,
   transcripts stay on disk, and fill the gaps.
3. Reality check in one round: branch, HEAD, status and diff stat of each repo against the file;
   `resume_file.py hash` on every owned file against the recorded prints; ListAgents; free RAM, CPU
   and disk against the resource rules.
4. Drift is a moved HEAD, another branch, or an owned file whose print changed, unless the change
   is the agent's own recorded work. Drift: AskUserQuestion before relaunching the agents it
   touches, the others start meanwhile. An accepted drift goes into the brief as a known difference.
5. Depth 1 agents only, one by one: the brief of a parent lists its children and their reports.
   `Statut : termine` or `A relancer : non`: skip it, write why. File written by this same session
   (session d'origine equals `$CLAUDE_CODE_SESSION_ID`): SendMessage the RESUME-ALL text of
   `relaunch-brief.md` to the old id, then check as that file says. Otherwise, or when that fails:
   Agent with the same subagent_type, model and effort, description `<old description> (reprise)`,
   prompt filled from `relaunch-brief.md`, in the background. Unknown model or effort (the digest
   prints `default`, the file says `inconnu`): leave that parameter out, never swap in another model.
   A type that no longer exists: general-purpose, same model.
6. Order: independent agents start together, four at most at once, the next one when a slot frees.
   `apres l'agent <id>` means after that agent finished and its result was checked. Two agents owning the
   same file never run at the same time.
7. Relaunch the processes marked to relaunch, only when an agent or your own part needs them, and
   close them at the end of the task.
8. Right after the launches, edit resume.md: a `## Reprise du <date>` section above `## Journal`
   with the new session id, old id to new id or `SendMessage`, skipped agents and why, agents
   waiting for another, drift found. Set `Etat : REPRIS le <date>, session <id>`, add the Journal
   line, run `resume_file.py log "<path>" resume`. The file stays, marked REPRIS.
9. Check: ListAgents shows every agent started now. A launch that failed is retried once, then
   written in resume.md and told to the user.
10. Delete the scratch folder. Take back your own part from `## Session principale`. Answer in
    three or four French lines.
