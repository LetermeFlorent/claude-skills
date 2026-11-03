# Installing claude-skills

This guide is for an AI agent running in Claude Code on the user's machine. Run each step, read its
output, and tell the user what happened.

## What gets installed

The repository holds 10 skills, one folder each with a `SKILL.md`, and the slash commands that start
them, in each skill's `commands/` folder. Installing clones the repository into the Claude Code
configuration folder, links every skill folder into its `skills/` folder and copies every command
into its `commands/` folder. When OpenCode is installed (`~/.config/opencode` exists), the commands are
also copied into `~/.config/opencode/commands/`. Nothing else outside the configuration folder changes.

Below, `<config>` is that folder: the value of `CLAUDE_CONFIG_DIR` when the variable is set, else
`~/.claude`. In a shell it reads `"${CLAUDE_CONFIG_DIR:-$HOME/.claude}"`.

## Requirements

Check both before cloning.

- git: `git --version`.
- Python 3.10 or later: `python --version`. Where `python` is missing or older, try `python3`, and
  use the one that works in every command below.

Skills are linked through directory junctions on Windows, which need no administrator rights, and
through symbolic links on macOS and Linux. `chrome-bidi` drives Chrome on Windows only; the other nine
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
   `skipped` with the reason, then one line for each hook it adds to `<config>/settings.json` (update and resource).
   Exit code 0 means everything is in place, 1 that at least one line was skipped or failed, 2 that
   the clone is not in `<config>/claude-skills`.
3. A `skipped` line means the user already has a skill or a command with that name. Never move or
   delete it yourself: show the line to the user and ask. If they want the version from this
   repository, they move theirs away and you run step 2 again.
4. A `not linked` line ends with the command that creates the link by hand. Show it to the user.
5. Tell the user to open a new Claude Code session: skills and commands are read when a session
   starts.

## Check

`ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"` lists the 10 skill folders and
`ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/commands"` the 11 command files, next to whatever the user
had before. Then run the update check once:

```bash
python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"
```

It prints `claude-skills: up to date (<version>)`.

## Commands

Each command starts one skill.

| Command | Skill |
|---|---|
| `/strip-ai-traces` | strip-ai-traces |
| `/chrome-bidi` | chrome-bidi |
| `/clean-code` | clean-code |
| `/commit` | clean-commits |
| `/stop-all`, `/resume-all` | stop-resume-agents |
| `/isolate` | using-git-worktrees |
| `/limited-run` | limited-run |
| `/model-effort` | model-effort |
| `/resource-guard` | resource-guard |
| `/write-skill` | writing-skills |

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

It removes the links, the commands it installed and its two hooks, and leaves alone any command the
user edited.
Once it has printed its lines, the folder `<config>/claude-skills` can be deleted.

## When something fails

A line `claude-skills: <type>: <message>` is an error the scripts did not plan for, and the line
after it says what to do by hand. Show both to the user.
