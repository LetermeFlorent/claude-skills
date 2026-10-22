---
name: chrome-bidi
description: Use when a task needs a web page opened, read, clicked, filled, screenshotted, printed or measured on this machine, when the user types /test-visuel, when a page must be checked at phone and desktop widths, when image sizes on a page must be compared with their files, or when a Chrome or chromedriver left by an earlier task has to be found and closed.
---

# Chrome over WebDriver BiDi

## Overview

Once per session, before following this skill, run
`python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"` and read the line it prints.
When that file does not exist, go on without it. After a line that starts with `updated`, read this file again
before going on.

Chrome is the only browser driven here, unless the user's instructions (CLAUDE.md) say otherwise.
The scripts start it with a debugging port and a throwaway profile, start a chromedriver of the same version
on port + 1000, and talk WebDriver BiDi to it over a websocket. Everything runs headless: no window
reaches the user's screen unless the user asked to watch and `--visible` is passed.

File names below sit in this skill's base directory (shown when the skill loads, otherwise
`$CLAUDE_CONFIG_DIR/skills/chrome-bidi`, or `~/.claude/skills/chrome-bidi` when the variable is
empty). Call every script with `python -I` and an absolute path in double quotes, forward slashes.
Python standard library only, nothing to install. A failing script prints
`chrome-bidi: <Type>: <message>`, then a `by hand:` line saying how to do the same step without it,
and exits 1. Exit 2 means a question for the user (virtual desktop, see below).

| Script | Role |
|---|---|
| `scripts/launch.py` | starts Chrome and chromedriver, prints the port |
| `scripts/bidi.py` | one action on a running Chrome, then hands the session back |
| `scripts/measure_images.py` | box of every displayed image at several widths, to JSON |
| `scripts/visual_test.py` | the /test-visuel run: screenshots per width plus the image measures |

chromedriver lives in `bin/`. At each launch the script compares its version with the installed
Chrome and, only when the build differs, downloads the right one from Chrome for Testing.

## Rules that never bend

These hold for every task, whoever asks.

1. Headless by default, for every task, test and capture. `--visible` only when the user asked to
   watch the browser in this task. Never ask "headless or window?": the answer is headless.
2. One port per task, never shared. Profile `<temp>/claude-skills/chrome-<port>`, where `<temp>` is the system temp
   folder (`tempfile.gettempdir()`), downloads in `chrome-<port>-downloads`, session in
   `chrome-<port>.session`. Never the user's own profile.
3. Never stop a `chrome.exe` or `chromedriver.exe` whose command line lacks
   `--remote-debugging-port=<your port>` or `--port=<your port + 1000>`. One without it belongs to
   the user or to another session.
4. Act through native input only (`input.performActions`, `input.setFiles`, WebDriver element
   calls). JavaScript reads the page, it never clicks, types or scrolls.
5. Close with `bidi.py close --port <p>` before the task ends: it ends Chrome, stops chromedriver
   and frees both ports. Then check nothing of yours is left (procedure, step 5).
6. Before a launch, check free RAM, CPU load and disk activity (the user's instructions, CLAUDE.md). One Chrome
   at a time per session.
7. Never move, hide, resize or close a window you did not start.

## Procedure

The steps run in this order.

1. Start Chrome. The port is picked between 9300 and 9899 when `--port` is missing; reuse a fixed
   port only to get back a profile that is already signed in.

   ```bash
   S="<skill>/scripts"
   python -I "$S/launch.py" --url "http://127.0.0.1:3000"
   ```

   It prints `chrome started, pid X, port P, driver P+1000, profile ..., downloads ...` and the
   driver check. Other options: `--size 1280x720` (content area, the default), `--profile <dir>`,
   `--prompt dismiss|accept|ignore` (what happens to an alert nobody answers, `dismiss` by
   default), `--visible`, `--desktop`, `--login`.
2. Act: `python -I "$S/bidi.py" <action> [value] --port P [--tab n] [--frame <url part>]`. Each call
   reconnects to the same session, so the tab, its scroll and its forms stay as they were. Run one
   call at a time on a port.
3. Look with `shot` and read the image, rather than guessing from the DOM.
4. Close: `python -I "$S/bidi.py" close --port P`.
5. Check: no `chrome.exe` or `chromedriver.exe` whose command line holds your port.

   ```bash
   powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='chrome.exe' or Name='chromedriver.exe'\" | ? { \$_.CommandLine -match 'remote-debugging-port=P(?!\d)|--port=P1000(?!\d)' } | Select ProcessId,Name"
   ```

   Replace `P` and `P1000` with your two ports. An empty answer is the only acceptable one.

### /test-visuel

`/test-visuel <url or local folder> [widths]` checks a page at a phone and a desktop width.

1. Run the resource check of rule 6.
2. `python -I "$S/visual_test.py" "<target>" 390,1440`. Widths default to 390 and 1440, the
   height to 720 (`--height`). Add `--visible` only when the user wrote it. A local folder or file
   is served on 127.0.0.1 for the run, then the server stops.
3. The run goes into `<project>/.ia/chrome-bidi/<date-time>/`, and `.ia/` is added to
   `.git/info/exclude`. The project is the git root of the target folder, or of the current folder
   for a url; with no project at all it goes to `<temp>/claude-skills/chrome-bidi/`. It holds
   `shot-<width>.png` and `images.json`.
4. Read each shot, then the image lines the script flagged: `blurry` (file narrower than box times
   device pixel ratio), `heavy` (more than twice the needed width), `not loaded`.
5. Answer in a few lines: what looks broken at which width, which images to resize, the folder.
   Chrome is already closed by the script; run the check of step 5 above with the port it printed.

### Image measures alone

```bash
python -I "$S/measure_images.py" --url "<url or folder>" --widths 390,1440 --out "<file.json>"
```

One record per image and width: `width`, `dpr`, `src`, `kind` (`img` or `background`), `box`
(content box for an `<img>`, padding box for a background, CSS pixels), `natural` (file pixels),
`fit` (`object-fit` or `background-size`) and `selector`. Elements with an empty box are skipped.
Lazy images are switched to eager and awaited up to 5 s.

### Sign-in a human has to type

Google and Microsoft refuse a sign-in in a driven browser. The user asked for it, so a window is
fine: `launch.py --port <p> --login --visible --url <sign-in page>`. No remote control in that
mode. Once signed in, the user closes the window and you start again on the same port without
`--login`: the profile keeps the session, so a port signed in once stays signed in.

### Window mode, only with --visible

Chrome opens maximized on the virtual desktop of the host window (terminal or editor), through
the `VirtualDesktop` PowerShell module. Exit 2 with `VIRTUAL_DESKTOP_MODULE_MISSING` means the
module is absent: ask the user to install it, or rerun with `--desktop current`. Exit 2 with
`HOST_DESKTOP_UNKNOWN` lists the desktops: ask which one, rerun with `--desktop <n>`. Never guess.
In this mode never call `viewport` or `mobile`: the user watches a window that would shrink to a
small block in a corner.

## Actions

A value with two parts takes `|` between them. A selector starting with `/` or `(` is xpath,
anything else is CSS.

Tabs: `nav <url>` reuses the tab already on the same host, else a blank tab, else a new one, and
prints its index for `--tab`. `newtab [url]`, `tabs`, `activate`, `closetab` (refuses the last
tab), `url` (address and title), `back`, `forward`, `reload`, `close`.

Reading: `wait <selector>` polls until found or `--timeout` seconds (10), `wait <n>` pauses.
`find <css>`, `xpath <query>`, `text [selector]`, `html [n chars]`, `eval <expression>` (read
only). `console [s]` listens for messages logged after the call. `network [s] [all]` reloads and
lists the requests, failures only without `all`. `cookies`, `clearcookies`.

Input: `click <css>`, `clickxpath <xpath>` (the element is scrolled into view with a wheel first),
`clickxy x,y`, `hover x,y`, `scroll [delta][@x,y]`, `type [text]` (stdin when empty, for a
password), `key <name>[ xN]` with `enter tab escape up down left right backspace delete ctrl shift`
and combos like `ctrl+a`, `upload <selector>|<path>`, `prompt accept|dismiss[|text]`,
`rejectcookies`.

WebDriver element calls, top page only: `fill <selector>|<text>` (stdin when no text) and
`select <selector>|<option text>`, which clicks the `<option>` itself and fires `change`.

Capture: `shot <png>`, `fullshot <png>`, `elementshot <selector>|<png>`, `pdf <file>`.

Emulation: `viewport WxH`, `mobile` (390x844, ratio 3, Android user agent), `desktop`,
`geo lat,lon|off` (granted to the page origin only), `locale <fr-FR|off>`,
`timezone <Europe/Paris|off>`, then reload.

## Known traps

Each of these has broken a run before.

- Git Bash rewrites an argument starting with `/`: `/html/body` arrives as a path under
  `C:/Program Files/Git`. Prefix the call with `MSYS_NO_PATHCONV=1`, or write `(//button)[1]`.
- `shot` keeps 720 px of height at most. A taller viewport is scaled down and the factor printed:
  multiply coordinates read on the image by it before `clickxy` or `hover`.
- With the default `--prompt dismiss` an alert is closed before `prompt` can answer it. Launch with
  `--prompt ignore` when the task has to accept or type into one.
- `click` and `fill` take the first match. A hidden duplicate (two email fields, one hidden)
  gives "element not interactable": narrow the selector, or `clickxy` then `type`.
- A native `<select>` menu and the Windows "Save as" dialog live outside the page: use `select`,
  and look for downloads in `chrome-<port>-downloads`.
- In a window covered by another, `document.visibilityState` is `hidden` and keys get lost.
  `fill` still works there.
- One `nav` per page. To see whether something changed, `wait <selector>` or `shot`; a `reload`
  restarts loaders and can replay an expired sign-in.
- The profile refuses by default: geolocation, notifications, camera, microphone, third-party
  cookies. Lift one refusal for one origin when the task needs it, as `geo` does.
- The WebDriver HTTP API of the same session stays open: the id is in `chrome-<port>.session`,
  the endpoints under `http://127.0.0.1:<port+1000>/session/<id>/`. Use it only when an action is
  missing, and never `DELETE` that session: `close` does it.

Site notes: in a web chat app, an app warning may offer to open the app anyway; take that link, since the
"open in the browser tab" one can loop. In a ticket app, a `scroll` placed on the conversation panel moves it.

## Red flags

These thoughts mean you are about to break a rule above.

| Thought | Reality |
|---|---|
| "The user will want to see it" | Headless, unless the user asked for `--visible`. The headless shot has the same pixels. |
| "That chrome.exe has no window, it must be a leftover" | Only a command line holding your port is yours. |
| "A quick `element.click()` in `eval` is simpler" | A script event skips focus, hover and `isTrusted` checks. Native input passes them. |
| "I'll close it at the very end, after the next task" | `bidi.py close --port <p>` before this task ends. |
| "Two calls in parallel on the same port will go faster" | One call at a time on a port. |
| "Reload to see if it changed" | `wait` or `shot`. Reloads restart loaders and replay sign-ins. |
| "A viewport 2000 high shows everything" | The shot is scaled down. Scroll and shoot, or `fullshot` to archive. |
| "That port is free, take it" | Its profile may hold the user's own session. Pick another port. |
| "The old chromedriver in AppData works, point at it" | launch.py keeps the one in `bin/` matched to Chrome; let it. |

## Files

The folder holds four entry scripts and the modules they share.

`scripts/launch.py` starts Chrome and its chromedriver on a port, `scripts/bidi.py` runs every action
on that port, `scripts/measure_images.py` measures the box of every displayed image and `scripts/visual_test.py`
shoots a page at several widths and measures its images. `scripts/actions/` holds the actions, `scripts/core/` the session, the processes
and the binaries, `scripts/window/` the window placement, `bin/` the chromedriver and `tests/` the
unit tests. `commands/test-visuel.md` is the `/test-visuel` command and `LISEZMOI.md` the French notes.
