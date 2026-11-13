# progress-board

To install it, see `INSTALL.md` at the root of the repository.

A page on your own computer, http://127.0.0.1:8790, that shows how far each AI has got. Every project gets one line on a chart, from 0 % up to where it is now, ending on a small icon with the project's name. Beside the chart (below it in a narrow window), a list gives each project's percentage and current step. Several AIs can report at once; the page updates by itself as soon as one of them sends a number.

## Using the page

Everything is done with the mouse.

- Drag the chart with the mouse to go back in time; the two small arrows jump to the start or to now.
- Point at a project in the list to bring its line forward; click it (or its line) to center the chart on it and fade the others, click again to undo.
- The settings button in the top right corner opens two tabs: settings (how much time the width shows, when finished or forgotten projects leave the page, light or dark theme) and projects (remove one, or clear them all).

A finished project shows its end time in the list and leaves the page an hour later. A project nobody reports on for three days leaves too.

## How the AIs use it

An AI sends one tiny request per step, for example `/site-shop/40/tests`: the project, the percentage, and optionally the step. That is all; the time is taken by your computer. The drive-project skill (`/drive`) sends its percentage here after every finished task.

The installer makes the page start by itself every time you log in. If it is ever down, the AI starts it again with one command before reporting.

## Files

The server uses the Python standard library only. The page is built with React from Untitled UI and React Bits components; the built copy in `site/` is committed, so running the page needs no Node.

- `SKILL.md`: what the AI reads, how to report and how to start the page.
- `server.py`: the small local server and its `start` command.
- `lib/store.py`: the saved projects and the settings.
- `site/`: the built page (`index.html` and `assets/`), served as is.
- `web/`: the page's sources. After a change, `npm install` then `npm run build` in `web/` rebuilds `site/`; an open page reloads by itself.
- `tests/test_pure.py`: checks the saved projects and a throwaway server on a free port, with no network.
- `.state.json`: the saved projects, created on first use, never committed.

## What was tested

The React page was checked in headless Chrome on a throwaway server: light and dark, hover on a list row and on a point, a click on a row, both jump arrows while new reports arrived, the settings tabs, removing one project, clearing all, the empty page, a 560x420 window, and the hand cursor on every clickable element. Dragging was checked on the earlier page, not on this one. Fifteen fake agents sent 541 reports at once with no error. Restarting the server kept every project.

One run on Sonnet with the server stopped: the agent read the skill, got exit code 7 on its first report, ran `server.py start`, sent it again, then reported 0, each step and 100, every answer `ok`. It asked whether the step was needed on `0` and `100`; `SKILL.md` now says it is optional on every report.

Not tested: a full `/drive` run sending its percentages, macOS and Linux start at login.
