# Installing claude-skills

This guide is for an AI agent running in Claude Code on the user's machine. Run each step, read its
output, and tell the user what happened.

## What gets installed

The repository holds 18 skills, one folder each with a `SKILL.md`, and the slash commands that start
them, in each skill's `commands/` folder. Installing clones the repository into the Claude Code
configuration folder, links every skill folder into its `skills/` folder and copies every command
into its `commands/` folder. Nothing outside the configuration folder changes.

Below, `<config>` is that folder: the value of `CLAUDE_CONFIG_DIR` when the variable is set, else
`~/.claude`. In a shell it reads `"${CLAUDE_CONFIG_DIR:-$HOME/.claude}"`.

## Requirements

Check both before cloning.

- git: `git --version`.
- Python 3.10 or later: `python --version`. Where `python` is missing or older, try `python3`, and
  use the one that works in every command below.

Skills are linked through directory junctions on Windows, which need no administrator rights, and
through symbolic links on macOS and Linux. `chrome-bidi` drives Chrome on Windows only; the other 17
skills run on any of the three.

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
   `skipped` with the reason. Exit code 0 means everything is in place, 1 that at least one line was
   skipped or failed, 2 that the clone is not in `<config>/claude-skills`.
3. A `skipped` line means the user already has a skill or a command with that name. Never move or
   delete it yourself: show the line to the user and ask. If they want the version from this
   repository, they move theirs away and you run step 2 again.
4. A `not linked` line ends with the command that creates the link by hand. Show it to the user.
5. Tell the user to open a new Claude Code session: skills and commands are read when a session
   starts.

## Check

`ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"` lists the 18 skill folders and
`ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/commands"` the 19 command files, next to whatever the user
had before. Then run the update check once:

```bash
python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"
```

It prints `up to date (<sha>)`. That run counts as the check of the current session: when a skill asks
for it again in the same session, the script prints `already checked this session` and stops at once.

## Commands

Each command starts one skill.

| Command | Skill |
|---|---|
| `/anti-empreinte` | anti-empreinte |
| `/concevoir` | brainstorming |
| `/test-visuel` | chrome-bidi |
| `/clean-code` | clean-code |
| `/commit` | clean-commits |
| `/paralleliser` | dispatching-parallel-agents |
| `/finir` | finishing-a-development-branch |
| `/projet` | project-dev |
| `/appliquer-relecture` | receiving-code-review |
| `/relecture` | requesting-code-review |
| `/stop-all`, `/resume-all` | stop-resume-agents |
| `/executer` | subagent-driven-development |
| `/deboguer` | systematic-debugging |
| `/test-dabord` | test-driven-development |
| `/isoler` | using-git-worktrees |
| `/verifier` | verification-before-completion |
| `/planifier` | writing-plans |
| `/creer-skill` | writing-skills |

## Updates

Every `SKILL.md` opens its overview with a line asking the agent to run `tools/update.py` once per
session, before following the skill. The script works in this order:

- it stops at once when it already ran in this Claude Code session (`CLAUDE_CODE_SESSION_ID`), or in
  the last 12 hours when that variable is missing;
- it asks GitHub for the latest commit of `main` and, when that commit is newer, fast-forwards the
  clone, links new skills, copies changed commands and removes what left the repository;
- it leaves a clone with local edits or local commits untouched, and says so;
- it keeps the current version when GitHub gives no answer within 20 seconds.

After a line that starts with `updated`, re-read the `SKILL.md` of the skill in use, since it may
have changed. Every planned outcome exits 0, so the skill goes on in every case. Running the line
again for a second skill in the same session costs nothing, since only the first run asks GitHub. To
update by hand, run the same command.

## Uninstall

```bash
python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/install.py" --uninstall
```

It removes the links and the commands it installed, and leaves alone any command the user edited.
Once it has printed its lines, the folder `<config>/claude-skills` can be deleted.

## When something fails

A line `claude-skills: <type>: <message>` is an error the scripts did not plan for, and the line
after it says what to do by hand. Show both to the user.
