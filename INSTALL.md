# Installing claude-skills

This guide is for an AI agent running in Claude Code on the user's machine. Run each step, read its
output, and tell the user what happened.

## What gets installed

The repository holds 13 skills, one folder each with a `SKILL.md`, and the slash commands that start
them, in each skill's `commands/` folder. Installing clones the repository into the Claude Code
configuration folder, links every skill folder into its `skills/` folder and copies every command
into its `commands/` folder. When OpenCode is installed (`~/.config/opencode` exists), the commands are
also copied into `~/.config/opencode/commands/`.

Three outside tools come with it, each kept at its latest version (see "Ponytail", "Graphify" and
"Caveman"): [Ponytail](https://github.com/DietrichGebert/ponytail), always on at its highest level,
[graphify](https://github.com/Graphify-Labs/graphify), used on large projects only, and the code search
agents of [caveman](https://github.com/JuliusBrussee/caveman), used on small projects. None goes through a
plugin, an MCP server or a connector.

Below, `<config>` is that folder: the value of `CLAUDE_CONFIG_DIR` when the variable is set, else
`~/.claude`. In a shell it reads `"${CLAUDE_CONFIG_DIR:-$HOME/.claude}"`.

## Requirements

Check git and Python before cloning; the other two are needed by one tool each.

- git: `git --version`.
- Python 3.10 or later: `python --version`. Where `python` is missing or older, try `python3`, and
  use the one that works in every command below.
- Node.js, for the Ponytail hooks: `node --version`. Without it the Ponytail skills still install.
- pip (shipped with Python) or uv, for graphify, which is installed with `uv tool install` when uv is
  found, else with `pip install --user`.

Skills are linked through directory junctions on Windows, which need no administrator rights, and
through symbolic links on macOS and Linux. `browser-bidi` drives Chrome or Firefox on Windows only; the other twelve
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
   `skipped` with the reason, then the Ponytail, caveman and graphify lines, then one line for each hook it adds
   to `<config>/settings.json` (update, resource and the three Ponytail hooks), then the progress-board line:
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

`ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"` lists the 13 skill folders, the six Ponytail ones, the two caveman ones and graphify,
`ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents"` the three `cavecrew-*.md` agents, and
`ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/commands"` the 13 command files, next to whatever the user
had before. Then run the update check once:

```bash
python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"
```

It prints `claude-skills: up to date (<version>)`, then `ponytail: up to date (<version>)`,
`caveman: up to date (<version>)`, `progress-board: http://127.0.0.1:8790 already running, starts at every login`
and `graphify: up to date (<version>)`.

## Commands

Each command starts one skill.

| Command | Skill |
|---|---|
| `/strip-ai-traces` | strip-ai-traces |
| `/browser-bidi` | browser-bidi |
| `/clean-code` | clean-code |
| `/commit` | clean-commits |
| `/drive` | drive-project |
| `/stop-all`, `/resume-all` | stop-resume-agents |
| `/isolate` | using-git-worktrees |
| `/limited-run` | limited-run |
| `/claude-model-effort` | claude-model-effort |
| `/other-model-effort` | other-model-effort |
| `/resource-guard` | resource-guard |
| `/write-skill` | writing-skills |

`/commit` and `/drive` push to GitHub through `clean-commits/scripts/push.py`. Set `CLAUDE_SKILLS_ACCOUNTS`
to the full path of an accounts tool, in the `env` block of `<config>/settings.json`, and the push takes its
token from that tool, as `clean-commits/SKILL.md` describes. Without it the push uses the user's own
credential helper.

## Updates

The installer adds a `SessionStart` hook (matcher `startup`) to `<config>/settings.json` that runs
`tools/update.py` each time Claude Code opens. The script:

- asks GitHub for the highest release tag `vX.Y.Z`; commits pushed to `main` without a release are
  ignored;
- when that release is newer than the clone, fetches it, fast-forwards, links new skills, copies
  changed commands and removes what left the repository, then prints
  `claude-skills: updated <old> to <new>: <skills>`;
- leaves a clone with local edits or local commits untouched, and says so;
- keeps the installed version when GitHub gives no answer within 20 seconds;
- never opens a login window: the credential helper is switched off for these calls.

Every planned outcome exits 0. To update by hand, run the same command.

To publish a version, create a release on GitHub (or push an annotated tag) with a higher
`vX.Y.Z` number.

## Ponytail

[Ponytail](https://github.com/DietrichGebert/ponytail) makes the agent write the smallest change that
fully solves the task. Its own install is a Claude Code plugin; this repository does it without one, so
that every account and OpenCode share the same copy:

- `install.py` and `update.py` ask GitHub for Ponytail's highest release tag and check it out into
  `<config>/ponytail`, a shallow clone, fetching again only when a newer release appears;
- its six skills (`ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`,
  `ponytail-help`) are linked into `<config>/skills`, and they are also its slash commands;
- three hooks run its own scripts with Node.js: `SessionStart` loads the rules at the active level,
  `SubagentStart` passes them to subagents, `UserPromptSubmit` follows `/ponytail <level>`;
- the default level is set to `ultra`, the highest, in Ponytail's `config.json` (`%APPDATA%/ponytail` on
  Windows, `~/.config/ponytail` elsewhere) and put back on every session start, so it is always on and
  at its maximum;
- for OpenCode, its commands go to `~/.config/opencode/commands/`, and its rules at the `ultra` level are
  written to `~/.config/opencode/ponytail-ultra.md` and listed under `instructions` in the OpenCode
  config file.

Ponytail marks a deliberate shortcut with a `shortcut:` comment, which the `clean-code` skill flags as
a comment in code. To keep code free of them, add this line to your `CLAUDE.md` or `AGENTS.md`, as
Ponytail's own FAQ suggests: "Never write `shortcut:` comments; name each shortcut in the reply."

The variable `CLAUDE_SKILLS_PONYTAIL_URL` points the checkout at another copy of the repository.

## Caveman

[caveman](https://github.com/JuliusBrussee/caveman) ships subagents that find, edit and review code and
send back very short reports, so the main session keeps its context. Its own install for Claude Code is a
plugin; this repository takes only the search part, without one:

- `install.py` and `update.py` ask GitHub for caveman's highest release tag and check it out into
  `<config>/caveman`, a shallow clone, fetching again only when a newer release appears;
- two of its skills are linked into `<config>/skills`: `cavecrew`, which says when to hand a search, a
  one or two file edit or a diff review to its agents, and `caveman-explore`, a read-only explorer;
- its three agents (`cavecrew-investigator`, `cavecrew-builder`, `cavecrew-reviewer`) are copied into
  `<config>/agents` and kept in step on every update; an agent you edited by hand is left alone;
- its caveman voice, hooks, status line and MCP server are left out: the voice would fight the
  language rules of your `CLAUDE.md`.

Use it on small projects, where graphify costs more than it saves: the AI hands "where is X, what calls
Y" to `cavecrew-investigator` and a review of its diff to `cavecrew-reviewer`, and gets a `path:line`
list back instead of pages of prose. The drive-project skill does this on its own.

The variable `CLAUDE_SKILLS_CAVEMAN_URL` points the checkout at another copy of the repository.

## Graphify

[graphify](https://github.com/Graphify-Labs/graphify) turns a codebase into a knowledge graph the agent
queries instead of reading files one by one. It only pays off on a large project, so this repository
installs it that way:

- the `graphifyy` package from PyPI is installed with uv or pip, then graphify's own installer writes
  its skill into a throwaway folder, and the skill is copied to `<config>/skills/graphify`;
- the skill description is narrowed to large codebases (about 300 tracked source files, 50,000 lines,
  a monorepo), a folder that already holds `graphify-out/`, or `/graphify`. The agent sees it in every
  session and leaves it aside on small projects;
- graphify's own installer is never run on the real configuration folder: it would add a section to
  `CLAUDE.md` and, for OpenCode, a plugin, which would turn it on everywhere;
- on every session start `update.py` compares the PyPI version with the installed one and, when it is
  newer, upgrades in the background at low priority, writing to `claude-skills/.ia/graphify.log`.

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

It removes the links, the commands it installed, its hooks, the Ponytail and caveman checkouts, the
caveman agents and the graphify skill, and leaves alone any command the user edited. The `graphifyy` package stays installed:
`pip uninstall graphifyy` (or `uv tool uninstall graphifyy`) removes it.
Once it has printed its lines, the folder `<config>/claude-skills` can be deleted.

## When something fails

A line `claude-skills: <type>: <message>` is an error the scripts did not plan for, and the line
after it says what to do by hand. Show both to the user.
