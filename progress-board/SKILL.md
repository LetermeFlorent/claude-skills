---
name: progress-board
description: Use when a run reports its percentage (the drive-project skill, a long task, several agents at once), when the user asks to see progress on the local page or the board, when http://127.0.0.1:8790 does not answer, or when curl to it fails with "connection refused" or exit code 7.
---

# Reporting progress to the local board

A local page, http://127.0.0.1:8790, draws one line per project: its percentage over time, the last
point marked by the project's icon and name, a card per project below. An agent reports with one short
GET request and nothing else. The server stamps the time itself, keeps the history on disk and pushes
each change to every open page.

`<board>` below is `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/progress-board`.

## Report

```bash
curl -s "http://127.0.0.1:8790/<project>/<percent>/<step>"
```

The answer is `ok`. In PowerShell call `curl.exe`, never `curl` (an alias of `Invoke-WebRequest` there).

| Part | Rule |
|---|---|
| `<project>` | The project folder's name, the same for the whole run (`site-shop`, `mod-minecraft`). Letters, digits, hyphens. |
| `<percent>` | A whole number from 0 to 100. |
| `<step>` | Optional on every report, `0` and `100` included; one to three words joined by hyphens (`tests`, `write-docs`). Never a space, a slash or a sentence. |

1. Send `0` when the work starts, then the new percentage after each finished step, then `100` once when
   the run is done. One request per change, never a loop and never a request just to say nothing changed.
2. Never send a time, a date or a query string: the server takes its own clock when the request arrives.
3. A percentage may go down when work turns out larger than planned; send the real value.
4. Several agents on one project send under the same `<project>` only when one of them owns the
   percentage (the drive-project lead). Otherwise each agent reports its own project name.
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
is safe to run any time: it never starts a second server. When it still fails, go on with the work without
the board and mention it in the final answer only; the board is never a reason to stop a run.

## What the user sees and controls

The page follows the system theme and has a settings window (time shown on the width, delay before a
finished project leaves, delay before a project with no news leaves, theme, removing projects). Those are
the user's: an agent never changes them. Defaults: a finished project leaves after 1 hour, a project with
no report for 3 days leaves too. A project reporting again after that comes back with its old icon and
color on a new line.

The installer (`tools/install.py`) sets the server to start at every login and starts it at once;
`--uninstall` removes the start at login. The data lives in `<board>/.state.json`.
