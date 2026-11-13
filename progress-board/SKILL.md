---
name: progress-board
description: Use when a run reports its percentage (the drive-project skill, a long task, several agents at once), when the user asks to see progress on the local page or the board, when http://127.0.0.1:8790 does not answer, or when curl to it fails with "connection refused" or exit code 7.
---

# Reporting progress to the local board

Local page http://127.0.0.1:8790 draws one line per project: percentage over time, last point marked by
project's icon and name, one card per project below. Agent reports with one short GET request, nothing else.
Server stamps time itself, keeps history on disk, pushes each change to every open page.

`<board>` below = folder of this SKILL.md (base directory Skill tool prints).

## Report

```bash
curl -sS "http://127.0.0.1:8790/<project>/<percent>/<step>"
```

Answer is `ok`. In PowerShell call `curl.exe`, never `curl` (alias of `Invoke-WebRequest` there).

| Part | Rule |
|---|---|
| `<project>` | Project folder's name, same for whole run (`site-shop`, `mod-minecraft`), never a path: lowercased, each run of characters other than a-z and 0-9 turned into one hyphen (`Mon Site_v2` gives `mon-site-v2`). |
| `<percent>` | Whole number from 0 to 100. |
| `<step>` | Optional on every report, `0` and `100` included; one to three words joined by hyphens (`tests`, `write-docs`). Never a space, a slash or a sentence. |

1. Send `0` when work starts, then new percentage after each finished step, then `100` once when run is done.
   One request per change, never a loop, never a request just to say nothing changed.
2. Never send a time, a date or a query string: server takes own clock when request arrives.
3. Percentage may go down when work turns out larger than planned; send real value.
4. In drive-project run only lead reports; workers and sub-workers never call board. Elsewhere, several agents
   on one project send under same `<project>` only when one of them owns percentage; otherwise each agent
   reports own project name.
5. Answer stays out of chat. Reporting never adds a word to what user reads.
6. Never post to board's settings routes (`/_cfg`, `/_del/...`, `/_clear`): user runs them from page.

## When the page does not answer

`curl` fails (exit code 7, "connection refused", "Failed to connect"), or user says page is unavailable:

```bash
python -I "<board>/server.py" start
```

Answers `http://127.0.0.1:8790 started` or `... already running`, then send report again, once. Safe any
time: never starts a second server. Server is shared, stays up: never stop it, even when this run started it.
Still fails: send no more reports for rest of run, go on with work without board, mention it in final answer
only; board is never a reason to stop a run.

## Start at login

Server starts at every login (set by `tools/install.py`), keeps data in `<board>/.state.json`; agent never
edits that file.
