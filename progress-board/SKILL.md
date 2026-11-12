---
name: progress-board
description: Use when a run reports its percentage (the drive-project skill, a long task, several agents at once), when the user asks to see progress on the local page or the board, when http://127.0.0.1:8790 does not answer, or when curl to it fails with "connection refused" or exit code 7.
---

# Reporting progress to the local board

A local page, http://127.0.0.1:8790, draws one line per project: its percentage over time, the last
point marked by the project's icon and name, a card per project below. An agent reports with one short
GET request and nothing else. The server stamps the time itself, keeps the history on disk and pushes
each change to every open page.

`<board>` below is the folder this SKILL.md is in (the base directory the Skill tool prints).

## Report

```bash
curl -sS "http://127.0.0.1:8790/<project>/<percent>/<step>"
```

The answer is `ok`. In PowerShell call `curl.exe`, never `curl` (an alias of `Invoke-WebRequest` there).

| Part | Rule |
|---|---|
| `<project>` | The project folder's name, the same for the whole run (`site-shop`, `mod-minecraft`), never a path: lowercased, each run of characters other than a-z and 0-9 turned into one hyphen (`Mon Site_v2` gives `mon-site-v2`). |
| `<percent>` | A whole number from 0 to 100. |
| `<step>` | Optional on every report, `0` and `100` included; one to three words joined by hyphens (`tests`, `write-docs`). Never a space, a slash or a sentence. |

1. Send `0` when the work starts, then the new percentage after each finished step, then `100` once when
   the run is done. One request per change, never a loop and never a request just to say nothing changed.
2. Never send a time, a date or a query string: the server takes its own clock when the request arrives.
3. A percentage may go down when work turns out larger than planned; send the real value.
4. In a drive-project run only the lead reports; workers and sub-workers never call the board.
   Elsewhere, several agents on one project send under the same `<project>` only when one of them
   owns the percentage; otherwise each agent reports its own project name.
5. The answer stays out of the chat. Reporting never adds a word to what the user reads.
6. Never post to the board's settings routes (`/_cfg`, `/_del/...`, `/_clear`): the user runs them from the
   page.

## When the page does not answer

`curl` fails (exit code 7, "connection refused", "Failed to connect"), or the user says the page is
unavailable:

```bash
python -I "<board>/server.py" start
```

It answers `http://127.0.0.1:8790 started` or `... already running`, then send the report again, once. It
is safe to run any time: it never starts a second server. The server is shared and stays up: never stop
it, even when this run started it. When it still fails, send no more reports for the rest of this run:
go on with the work without the board and mention it in the final answer only; the board is never a
reason to stop a run.

## Start at login

The server starts at every login (set by `tools/install.py`) and keeps its data in `<board>/.state.json`;
an agent never edits that file.
