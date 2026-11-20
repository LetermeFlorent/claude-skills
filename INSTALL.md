# Installing claude-skills

This guide is for an AI agent running in Claude Code on the user's machine. Run each step, read its
output, and tell the user what happened.

## What gets installed

The repository holds 22 skills, one folder each with a `SKILL.md`, and the slash commands that start
them, in each skill's `commands/` folder. Installing clones the repository into the Claude Code
configuration folder, links every skill folder into its `skills/` folder and copies every command
into its `commands/` folder. When OpenCode is installed (`~/.config/opencode` exists), the commands are
also copied into `~/.config/opencode/commands/`.

Two hooks load the rules of the `terse-speech` and `least-code` skills at the start of every session and
of every subagent (see "Speech and code hooks"). Nothing goes through a plugin, an MCP server or a
connector. Earlier versions also installed Ponytail, caveman and graphify; the next run removes them (see
"Old outside tools").

Below, `<config>` is that folder: the value of `CLAUDE_CONFIG_DIR` when the variable is set, else
`~/.claude`. In a shell it reads `"${CLAUDE_CONFIG_DIR:-$HOME/.claude}"`.

## Requirements

Check git and Python before cloning.

- git: `git --version`.
- Python 3.10 or later: `python --version`. Where `python` is missing or older, try `python3`, and
  use the one that works in every command below.

Skills are linked through directory junctions on Windows, which need no administrator rights, and
through symbolic links on macOS and Linux. `browser-bidi` drives Chrome or Firefox on Windows only; the other sixteen
run on any of the three.

## Install

Five steps, in this order.

1. Clone the repository. The credential helper is switched off so that no login window opens for a
   public repository:

   ```bash
   git -c credential.helper= clone https://github.com/LetermeFlorent/claude-skills.git "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills"
   ```

   When that folder already exists, skip the clone and go to "Updates".
2. Run the installer:

   ```bash
   python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/install.py"
   ```

   It prints one line per skill and per command: `linked`, `copied`, `already there`, `removed`, or
   `skipped` with the reason, then one line for each hook it adds
   to `<config>/settings.json` (update, resource, and the two speech and code hooks), then the progress-board line:
   the local progress page at http://127.0.0.1:8790 is started and set to start at every login
   (Windows: the `Run` key of the current user; macOS: a LaunchAgent; Linux: `~/.config/autostart`).
   Exit code 0 means everything is in place, 1 that at least one line was skipped or failed, 2 that
   the clone is not in `<config>/claude-skills`.
3. A `skipped` line means the user already has a skill or a command with that name. Never move or
   delete it yourself: show the line to the user and ask. If they want the version from this
   repository, they move theirs away and you run step 2 again.
4. A `not linked` line ends with the command that creates the link by hand. Show it to the user.
5. Tell the user to open a new Claude Code session: skills and commands are read when a session
   starts.

## Check

`ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"` lists the 22 skill folders and
`ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/commands"` the 14 command files, next to whatever the user
had before. Then run the update check once:

```bash
python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"
```

It prints only what changed or failed, one `claude-skills: ` line each, so right after an install it
usually prints nothing.

## Commands

Each command starts one skill.

| Command | Skill |
|---|---|
| `/strip-ai-traces` | strip-ai-traces |
| `/browser-bidi` | browser-bidi |
| `/clean-code` | clean-code |
| `/clean-arch` | clean-architecture |
| `/commit` | clean-commits |
| `/drive` | drive-project |
| `/stop-all`, `/resume-all` | stop-resume-agents |
| `/isolate` | using-git-worktrees |
| `/limited-run` | limited-run |
| `/claude-model-effort` | claude-model-effort |
| `/other-model-effort` | other-model-effort |
| `/resource-guard` | resource-guard |
| `/write-skill` | writing-skills |
| `/secure-code-loop` | secure-code-loop |

`/commit` and `/drive` push to GitHub through `clean-commits/scripts/push.py`. Set `CLAUDE_SKILLS_ACCOUNTS`
to the full path of an accounts tool, in the `env` block of `<config>/settings.json`, and the push takes its
token from that tool, as `clean-commits/SKILL.md` describes. Without it the push uses the user's own
credential helper.

## Updates

The installer adds a `SessionStart` hook (matcher `startup`) to `<config>/settings.json` that runs
`tools/update.py` each time Claude Code opens. The script:

- asks GitHub at most once every six hours; the time of the last check is
  the date of `<config>/claude-skills/.ia/update-check.stamp`, so a second account opening sooner skips
  the network and only does the local steps below;
- asks GitHub for the highest release tag `vX.Y.Z`; commits pushed to `main` without a release are
  ignored;
- when that release is newer than the clone, fetches it, fast-forwards, links new skills, copies
  changed commands and removes what left the repository, then prints
  `claude-skills: updated <old> to <new>: <skills>`;
- leaves a clone with local edits or local commits untouched, and says so; a fast-forward that fails
  (a file git does not track is in the way) prints `claude-skills: could not install <tag>: <reason>`
  and the rest of the update still runs;
- links every skill folder of the clone at each run, even one committed locally without a release,
  and puts back the hooks;
- removes what the old outside tools left, every run, and prints a line for each thing it removes;
- prints nothing when everything is up to date, only what changed or failed;
- keeps the installed version when GitHub gives no answer within 20 seconds;
- never opens a login window: the credential helper is switched off for these calls.

Every planned outcome exits 0. To update by hand, delete `.ia/update-check.stamp` in the clone, then
run the same command.

The hooks hold the full path of the Python found at install time. After installing,
moving or removing a Python version, run `install.py` again: once the old Python is gone,
the update hook cannot start and cannot repair itself.

To publish a version, create a release on GitHub (or push an annotated tag) with a higher
`vX.Y.Z` number.

## Speech and code hooks

The installer adds two hooks that run `tools/inject.py`: a `SessionStart` hook (matcher
`startup|resume|clear|compact`) and a `SubagentStart` hook. The script reads `terse-speech/SKILL.md` and
`least-code/SKILL.md` from the clone, drops their front matter, and hands both texts to Claude Code as
extra context. So every session, and every subagent a session starts, begins with the same two rules:
answer short and plain, and write the smallest change that fully works.

A skill file that is missing is skipped. If neither exists, or anything goes wrong, the script prints an
empty answer and exits 0, so a session never shows a hook error. It does not wait for input from the
terminal.

## Old outside tools

Earlier versions installed Ponytail, caveman and graphify. Both `install.py` and `update.py` now remove
what they left, using the files the old installer kept in `<config>/claude-skills/.ia/`
(`ponytail.json`, `caveman.json`, `graphify.json`). On every run, and only for what those files list:

- the skill links that point into the old checkouts, and the two checkouts `<config>/ponytail` and
  `<config>/caveman`;
- the three `cavecrew-*` agents and the OpenCode commands and rules, but only when the file is still
  exactly what was copied; a file you edited stays, with one line saying so;
- Ponytail's mode file `config.json`, and its folder when it ends up empty;
- the `<config>/skills/graphify` folder, only when it holds the `.claude-skills` mark, and the
  `graphifyy` package, with `uv tool uninstall` when uv lists it, else `pip uninstall` when pip shows it,
  at low priority and with a time limit;
- any hook in `<config>/settings.json` whose command runs a script under `ponytail/hooks/`.

Each removal prints one line, and a run with nothing left prints nothing. When a removal fails, its file
in `.ia/` is kept and the next run tries again.

## Resource hook

The installer also adds a `PreToolUse` hook (matcher `Bash`) that runs
`resource-guard/scripts/guard.py hook` before every shell command. Light commands pass at once.
Heavy ones (builds, tests, docker, node, python...) wait until free RAM, CPU load and disk activity
are back under the thresholds, five minutes at most, then the call is blocked with the reason.
`resource-guard/SKILL.md` lists the thresholds and the variables that change them.

## OpenCode

OpenCode reads skills from `~/.claude/skills` on its own, so an install into `~/.claude` serves both.
The installer copies the commands into `~/.config/opencode/commands/` and keeps them in step on every
update; the variable `CLAUDE_SKILLS_OPENCODE_DIR` points it at another folder, or turns it off when
empty. OpenCode has no hook without a plugin, so it runs the resource check by hand: its instructions
file (`~/.config/opencode/AGENTS.md`, or `~/.claude/CLAUDE.md` when that file is missing) should tell
it to run `resource-guard/scripts/guard.py wait` before heavy commands.

## Uninstall

```bash
python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/install.py" --uninstall
```

It removes the links, the commands it installed and its hooks, and leaves alone any command the user
edited. It also cleans up the old outside tools, as above.
Once it has printed its lines, the folder `<config>/claude-skills` can be deleted.

## When something fails

A line `claude-skills: <type>: <message>` is an error the scripts did not plan for, and the line
after it says what to do by hand. Show both to the user.
