---
name: browser-bidi
description: Use when a page must be opened, read, clicked, filled, screenshotted, printed or measured in Chrome or Firefox, checked at phone and desktop widths (/browser-bidi), or its images checked for blurry or oversized files, or when a leftover Chrome, Firefox, chromedriver or geckodriver must be closed.
---

# Chrome or Firefox over WebDriver BiDi

The scripts start Chrome with a debugging port and a throwaway profile, a chromedriver of the same
version on port + 1000 (kept in `bin/`, downloaded from Chrome for Testing when the build differs),
and talk BiDi over a websocket. Chrome is the default; Firefox only when the user asks for it, with
`--browser firefox` on `launch.py`, `measure_images.py` or `visual_test.py`. Firefox is found through
its App Paths registry key, else under Program Files or LOCALAPPDATA, and starts with
`-marionette --remote-debugging-port=<port> -no-remote -profile <dir>`. `bin/geckodriver.exe`, from
the latest GitHub release when missing, attaches to it on port + 1000 with `--connect-existing`.
`bidi.py` reads the browser from the session file, so its calls stay the same.

Call every script as `python -I "<skill dir>/scripts/<name>.py"` with forward slashes. Stdlib only. A
failure prints `browser-bidi: <Type>: <message>` and a `by hand:` line, exit 1. A `PermissionError`
while the driver updates means another session's driver is running
from `bin/`: never stop it, and launch again once it is closed.

Scripts: `launch.py` (start, prints the port), `bidi.py` (one action on a running browser),
`measure_images.py` (box of every displayed image per width, JSON), `visual_test.py` (the /browser-bidi run).

## Rules

These hold for every task, whatever the page.

1. Pick the mode yourself and never ask about it. `--visible` when a person has to see or act in the
   window: a sign-in, a code or phone check, the user saying they want to watch. Headless for
   everything else (reading, checks, screenshots, /browser-bidi).
2. One port per task, never shared. Profile `<temp>/claude-skills/<browser>-<port>` (`chrome-9300`,
   `firefox-9300`), downloads in `<browser>-<port>-downloads`, session in `bidi-<port>.session`. Never
   the user's profile.
3. Never stop a `chrome.exe`, `firefox.exe`, `chromedriver.exe` or `geckodriver.exe` whose command
   line lacks `--remote-debugging-port=<your port>` or `--port=<your port + 1000>`: it belongs to the
   user or another session. Never move, hide, resize or close a window you did not start.
4. Native input only (`input.performActions`, `input.setFiles`, WebDriver element calls). JavaScript
   reads the page, it never clicks, types or scrolls.
5. Before a launch, run resource-guard's `guard.py wait` and launch only on exit 0. One browser at a
   time per session. `launch.py`, `measure_images.py` and `visual_test.py` run directly, never through
   limited-run, whose job would kill the browser as soon as `launch.py` returns. The browser runs
   detached, headless at below-normal priority, and `close` stops it.
6. Close with `bidi.py close --port P` before the task ends, then check nothing is left, then delete
   `<browser>-<port>` and `<browser>-<port>-downloads` unless the profile holds a sign-in kept on
   purpose.

## Procedure

Five steps, from launch to the leftover check.

1. `python -I "$S/launch.py" --url "http://127.0.0.1:3000"`, where `$S` is `<skill dir>/scripts` written
   out in full in each call (a shell variable does not last from one call to the next). Port picked
   in 9300-9899 when `--port` is missing; reuse a fixed port only to get back a signed-in profile.
   Options: `--browser firefox`, `--size 1280x720` (content area), `--profile <dir>`,
   `--prompt dismiss|accept|ignore` (unanswered alert, `dismiss` default), `--visible`, `--desktop`,
   `--login`. `already running` on a
   port this task did not launch means another task owns it: do not drive or close it.
2. `python -I "$S/bidi.py" <action> [value] --port P [--tab n] [--frame <url part>] [--timeout s]`.
   Each call reconnects to the same session. One call at a time per port.
3. Read the result of `shot` rather than guessing from the DOM.
4. `python -I "$S/bidi.py" close --port P`.
5. Check, replacing `P` with the port and `P1000` with port + 1000 (for example 9300 and 10300); empty
   output is the only good one:

   ```bash
   powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='chrome.exe' or Name='chromedriver.exe' or Name='firefox.exe' or Name='geckodriver.exe'\" | ? { \$_.CommandLine -match 'remote-debugging-port=P(?!\d)|--port=P1000(?!\d)' } | Select ProcessId,Name"
   ```

   A pid still listed (for example a driver whose browser is gone, which `close` refuses):
   `MSYS_NO_PATHCONV=1 taskkill /PID <pid> /T /F` on those pids only.

### /browser-bidi

`/browser-bidi <url or local folder> [widths]`.

1. `python -I "$S/visual_test.py" "<target>" 390,1440`. Widths default to 390,1440, height 720
   (`--height`), `--visible` and `--browser firefox` only if the user wrote them. A local folder or
   file is served on 127.0.0.1 during the run.
2. Output goes to `<project>/.ia/browser-bidi/<date-time>/` (`shot-<width>.png`, `images.json`),
   `.ia/` added to `.git/info/exclude`. Project is the git root of the target, or of the current
   folder for a url; with none, `<temp>/claude-skills/browser-bidi/`.
3. Read each shot and the flagged image lines: `blurry` (file narrower than box times dpr),
   `heavy` (over twice the needed width), `not loaded`.
4. Answer in a few lines: what breaks at which width, images to resize, the folder. The script
   already closed the browser; run step 5 of the Procedure with the port it printed.

### Image measures alone

```bash
python -I "$S/measure_images.py" --url "<url or folder>" --widths 390,1440 --out "<file.json>"
```

Per image and width: `width`, `dpr`, `src`, `kind` (`img` or `background`), `box` (content box for
`<img>`, padding box for a background, CSS px), `natural`, `fit`, `selector`. Empty boxes are
skipped; lazy images are made eager and awaited up to 5 s.

### Sign-in a human has to type

Google and Microsoft refuse a driven browser: `launch.py --port <p> --login --visible --url <page>`,
no remote control. The user signs in and closes the window; start again on the same port without
`--login`, the profile keeps the session.

### Window mode (--visible)

The browser opens maximized on the virtual desktop of the host window when the `VirtualDesktop`
PowerShell module is there and that desktop can be found, else on the desktop shown now. Nothing to
ask. `--desktop <n>` forces one. Never call `viewport` or `mobile` in this mode.

## Actions

Two-part values use `|`. A selector starting with `/` or `(` is xpath, else CSS.

- Tabs: `nav <url>` (reuses the tab on the same host, else a blank one, else a new one; prints the
  index for `--tab`), `newtab [url]`, `tabs`, `activate`, `closetab` (refuses the last), `url`,
  `back`, `forward`, `reload`, `close`.
- Reading: `wait <selector>` (polls up to `--timeout`, 10) or `wait <n>`, `find <css>`,
  `xpath <query>`, `text [selector]`, `html [n chars]`, `eval <expression>` (read only),
  `console [s]` (messages logged after the call), `network [s] [all]` (reloads, failures only
  without `all`), `cookies`, `clearcookies`.
- Input: `click <css>`, `clickxpath <xpath>`, `clickxy x,y`, `hover x,y`, `scroll [delta][@x,y]`,
  `type [text]` (stdin when empty, for a password), `key <name>[ xN]` (`enter tab escape up down
  left right backspace delete ctrl shift`, combos like `ctrl+a`), `upload <selector>|<path>`,
  `prompt accept|dismiss[|text]`, `rejectcookies`, `fill <selector>|<text>` (stdin when no text),
  `select <selector>|<option text>`. `fill` and `select` are WebDriver element calls, top page only.
- Capture: `shot <png>`, `fullshot <png>`, `elementshot <selector>|<png>`, `pdf <file>`.
- Emulation, then reload: `viewport WxH`, `mobile` (390x844, ratio 3, Android UA), `desktop`,
  `geo lat,lon|off` (page origin only), `locale <fr-FR|off>`, `timezone <Europe/Paris|off>`.

## Traps

Each of these has cost a run before.

- Git Bash rewrites an argument starting with `/`: prefix with `MSYS_NO_PATHCONV=1` or write
  `(//button)[1]`.
- Every capture fits in 1024 px of width and `shot` in 720 px of height; a larger one is scaled down
  and the factor printed. Multiply coordinates read on a `shot` by it before `clickxy` or `hover`.
- `--prompt dismiss` closes an alert before `prompt` can answer: launch with `--prompt ignore`.
- `click` and `fill` take the first match; a hidden duplicate gives "element not interactable".
  Narrow the selector, or `clickxy` then `type`.
- A native `<select>` menu and the Windows "Save as" dialog live outside the page: use `select`;
  downloads land in `<browser>-<port>-downloads`.
- In a covered window `document.visibilityState` is `hidden` and keys get lost; `fill` still works.
- One `nav` per page. `reload` restarts loaders and can replay an expired sign-in: use
  `wait <selector>` or `shot` to see a change.
- The profile refuses geolocation, notifications, camera, microphone and third-party cookies.
- The WebDriver HTTP API of the session stays open (id in `bidi-<port>.session`, endpoints under
  `http://127.0.0.1:<port+1000>/session/<id>/`). Use it only for a missing action, never `DELETE`
  the session: `close` does it.
- Firefox refuses `browser.close` in a session opened through geckodriver, so `close` stops it by its
  own pids: `forced pids` in its output is the normal end for Firefox. `-no-remote` and the own profile
  keep it apart from a Firefox the user has open.
- Web chat app: take the "open the app anyway" link, the "open in the browser tab" one can loop.
  Ticket app: a `scroll` placed on the conversation panel moves it.
