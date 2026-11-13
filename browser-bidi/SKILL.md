---
name: browser-bidi
description: Use when a page must be opened, read, clicked, filled, screenshotted, printed or measured in Chrome or Firefox, checked at phone and desktop widths (/browser-bidi), or its images checked for blurry or oversized files, or when a leftover Chrome, Firefox, chromedriver or geckodriver must be closed.
---

# Chrome or Firefox over WebDriver BiDi

Scripts start Chrome with debugging port and throwaway profile, plus chromedriver of same version on
port + 1000 (kept in `bin/`, downloaded from Chrome for Testing when build differs), and talk BiDi over
websocket. Chrome by default; Firefox only when user asks, with `--browser firefox` on `launch.py`,
`measure_images.py` or `visual_test.py`. `bidi.py` reads browser from session file, so its calls stay same.

Call every script as `python -I "<skill dir>/scripts/<name>.py"` with forward slashes. Stdlib only.
Failure prints `browser-bidi: <Type>: <message>` and `by hand:` line, exit 1. `PermissionError` while
driver updates = another session's driver runs from `bin/`: never stop it, launch again once it is closed.

Scripts: `launch.py` (start, prints port), `bidi.py` (one action on running browser),
`measure_images.py` (box of every displayed image per width, JSON), `visual_test.py` (the /browser-bidi run).

## Rules

These hold for every task, whatever the page.

1. Pick mode yourself, never ask. `--visible` when a person must see or act in window: sign-in, code or
   phone check, user says they want to watch. Headless for everything else (reading, checks,
   screenshots, /browser-bidi).
2. One port per task, never shared. Profile `<temp>/claude-skills/<browser>-<port>` (`chrome-9300`,
   `firefox-9300`), downloads in `<browser>-<port>-downloads`, session in `bidi-<port>.session`. Never
   user's profile.
3. Never stop a `chrome.exe`, `firefox.exe`, `chromedriver.exe` or `geckodriver.exe` whose command
   line lacks `--remote-debugging-port=<your port>` or `--port=<your port + 1000>`: belongs to user or
   another session. Never move, hide, resize or close a window you did not start.
4. Native input only (`input.performActions`, `input.setFiles`, WebDriver element calls). JavaScript
   reads page, never clicks, types or scrolls.
5. resource-guard hook holds `launch.py`, `measure_images.py` and `visual_test.py`; where no hook runs,
   run `python -I ~/.claude/claude-skills/resource-guard/scripts/guard.py wait` first, launch only on
   exit 0. One browser at a time per session. These three run directly, never through limited-run,
   whose job would kill browser as soon as `launch.py` returns. Browser runs detached, headless at
   below-normal priority; `close` stops it.
6. Close with `bidi.py close --port P` before task ends, check nothing is left, then delete
   `<browser>-<port>` and `<browser>-<port>-downloads` unless profile holds a sign-in kept on purpose.

## Procedure

Five steps, from launch to leftover check.

1. `python -I "$S/launch.py" --url "http://127.0.0.1:3000"`, `$S` = `<skill dir>/scripts` written out
   in full in each call (shell variable does not last between calls). Port picked in 9300-9899 when
   `--port` missing; reuse fixed port only to get back a signed-in profile. Options: `--browser firefox`,
   `--size 1280x720` (content area), `--prompt dismiss|accept|ignore` (unanswered alert, `dismiss`
   default), `--visible`, `--desktop`, `--login`. `already running` on a port this task did not launch =
   another task owns it: do not drive or close it.
2. `python -I "$S/bidi.py" <action> [value] --port P [--tab n] [--frame <url part>] [--timeout s]`.
   Each call reconnects to same session. One call at a time per port.
3. Read result of `shot` rather than guessing from DOM.
4. `python -I "$S/bidi.py" close --port P`. Works even when browser or driver already died.
5. Check: `close` line must end with `nothing left`. On `pids [...] still running`:
   `MSYS_NO_PATHCONV=1 taskkill /PID <pid> /T /F` on those pids only.

### /browser-bidi

`/browser-bidi <url or local folder> [widths]`.

1. `python -I "$S/visual_test.py" "<target>" 390,1440`. Widths default 390,1440, height 720
   (`--height`), `--visible` and `--browser firefox` only if user wrote them. Local folder or file
   served on 127.0.0.1 during run.
2. Output to `<project>/.ia/browser-bidi/<date-time>/` (`shot-<width>.png`, `images.json`), `.ia/`
   added to `.git/info/exclude`. Project = git root of target, or of current folder for a url; with
   none, `<temp>/claude-skills/browser-bidi/`.
3. Read each shot and flagged image lines: `blurry` (file narrower than box times dpr; dpr 3 at widths
   up to 480, 2 above), `heavy` (over twice needed width), `not loaded`.
4. Answer in few lines: what breaks at which width, images to resize, folder. Script already closed
   browser; check its `browser closed` line ends with `nothing left` (Procedure step 5), else taskkill
   the listed pids.

### Image measures alone

```bash
python -I "$S/measure_images.py" --url "<url or folder>" --widths 390,1440 --out "<file.json>"
```

Per image and width: `width`, `dpr` (3 up to 480 px, else 2), `src`, `kind` (`img` or `background`),
`box` (content box for `<img>`, padding box for a background, CSS px), `natural`, `fit`, `selector`.
Empty boxes skipped; lazy images made eager and awaited up to 5 s.

### Sign-in a human has to type

Google and Microsoft refuse a driven browser: `launch.py --port <p> --login --visible --url <page>`,
no remote control. User signs in and closes window; start again on same port without `--login`,
profile keeps session.

### Window mode (--visible)

Browser opens maximized on virtual desktop of host window when `VirtualDesktop` PowerShell module is
there and that desktop can be found, else on desktop shown now. Nothing to ask. `--desktop <n>` forces
one. Never call `viewport` or `mobile` in this mode.

## Actions

Two-part values use `|`. Selector starting with `/` or `(` is xpath, else CSS. Value starting with `-`
goes after `--`: `bidi.py scroll --port P -- -600@100,200`.

- Tabs: `nav <url>` (reuses tab on same host, else a blank one, else a new one; prints index for
  `--tab`; later calls without `--tab` act on tab of last `nav` or `newtab`, else tab 0), `newtab [url]`, `tabs`,
  `activate`, `closetab` (refuses the last), `url`, `back`, `forward`, `reload`, `close`.
- Reading: `wait <selector>` (polls up to `--timeout`, 10) or `wait <n>`, `find <css>`,
  `xpath <query>`, `text [selector]` (20000 chars max), `html [n chars, 20000 by default]`,
  `eval <expression>` (read only), `console [s]` (messages logged after call), `network [s] [all]`
  (reloads, failures only without `all`), `cookies`, `clearcookies`.
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

- Git Bash rewrites argument starting with `/`: prefix with `MSYS_NO_PATHCONV=1` or write
  `(//button)[1]`.
- Every capture fits in 1024 px of width and `shot` in 720 px of height; larger one scaled down and
  factor printed. Multiply coordinates read on a `shot` by it before `clickxy` or `hover`.
- `--prompt dismiss` closes alert before `prompt` can answer: launch with `--prompt ignore`.
- `click` and `fill` take first match; hidden duplicate gives "element not interactable". Narrow
  selector, or `clickxy` then `type`.
- Native `<select>` menu and Windows "Save as" dialog live outside page: use `select`; downloads land
  in `<browser>-<port>-downloads`.
- In covered window `document.visibilityState` is `hidden` and keys get lost; `fill` still works.
- One `nav` per page. `reload` restarts loaders and can replay expired sign-in: use `wait <selector>`
  or `shot` to see a change.
- Profile refuses geolocation, notifications, camera, microphone and third-party cookies.
- WebDriver HTTP API of session stays open (id in `bidi-<port>.session`, endpoints under
  `http://127.0.0.1:<port+1000>/session/<id>/`). Use it only for a missing action, never `DELETE`
  session: `close` does it.
- Firefox refuses `browser.close` in session opened through geckodriver, so `close` stops it by its
  own pids: `forced pids` in output is normal end for Firefox. `-no-remote` and own profile keep it
  apart from a Firefox user has open.
- Web chat app: take "open the app anyway" link, "open in the browser tab" one can loop.
