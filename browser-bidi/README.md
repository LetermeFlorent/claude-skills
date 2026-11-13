# browser-bidi

A skill that drives Chrome, or Firefox when you ask for it, from Python (nothing to install) and the `/browser-bidi` command. To install it, see `INSTALL.md` at the root of the repository.

The AI decides on its own, without asking you: a visible window when someone has to see or act (signing in to a Google or Microsoft account, a verification code, or when you want to watch), no window for everything else.

`/browser-bidi https://example.com` (or a local folder, with other widths as an option: `360,768,1920`) opens the page at phone width (390) and desktop width (1440), captures each one, measures the images (blurry or too heavy) and closes the browser. Add `--browser firefox` to the request to do it in Firefox. The result goes to `.ia\browser-bidi\` at the project root, ignored by git on your machine only; outside a project, to `<temp>/claude-skills/browser-bidi/`.

`SKILL.md` holds the rules. `scripts` has four entry points (`launch`, `bidi`, `measure_images`, `visual_test`) and two module folders (`core` for the browser, the session and the processes, `actions` for the `bidi` commands). `tests` checks the small functions.
`bin\chromedriver.exe` is downloaded at launch when Chrome has changed version, `bin\geckodriver.exe` the first time Firefox is used. geckodriver is never updated after that: delete `bin\geckodriver.exe` to get the latest release.

Firefox is found through its App Paths registry key, else under Program Files or LOCALAPPDATA, and starts with `-marionette --remote-debugging-port=<port> -no-remote -profile <dir>`. `bin\geckodriver.exe` attaches to it on port + 1000 with `--connect-existing`.

Images are measured at a pixel density of 3 up to 480 px wide (a phone) and 2 above, so a file made only for a plain screen shows up as blurry.

## Not tested yet

The window mode on a virtual desktop has not been tried, because the `VirtualDesktop` module is missing. The pixel density set for the image measures has not been tried in a real Chrome or Firefox run.
