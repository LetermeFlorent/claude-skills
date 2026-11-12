# resource-guard

Several agents work at the same time on the same PC. When one starts a build, tests or docker while another does the same, everything crawls. This skill makes the agent wait until the machine has enough room. To install it, see `INSTALL.md` at the root of the repository.

## /resource-guard

Type `/resource-guard` to see the free memory, the processor load and the disk activity. Followed by a command, it waits until there is room, then runs it.

## What happens

Before each command, the agent checks whether it is heavy: a build, tests, docker, a development server, a package install. A light command (`git status`, `ls`) goes through right away, with nothing measured. A heavy command waits until at least 1.5 GB of memory is free, the processor runs below 85% and the disk is not saturated. After 5 minutes without room, the command is not started and the agent is told why.

Low on space on the current drive (under 20 GB)? A simple warning is shown, with no wait. Waiting does not free the disk, you have to clean up.

## By hand

`python -I "<folder>/scripts/guard.py" check` prints a status line and says whether things are fine. `wait` waits until they are. The thresholds can be changed with options or environment variables, listed in `SKILL.md`.

## With which agent

With Claude Code, the repository installer sets up the check by itself. Codex CLI and Qwen Code have the same kind of hook: `reference/wiring.md` gives the lines to paste into their configuration. For Gemini CLI and the others, a sentence in their instructions file asks them to run `wait` before a heavy command.

## What is in the folder

`scripts/guard.py` is the tool. `scripts/lib` holds the list of heavy commands, the reading of the incoming event, the thresholds and the measurement, with one file per system (Windows, Linux, macOS). `tests/test_pure.py` checks the list and the thresholds and runs a real measurement. `reference/wiring.md` holds the hook settings for agents other than Claude Code.
