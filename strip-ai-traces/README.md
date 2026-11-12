# strip-ai-traces

A skill and a command for Claude Code that keep a text, a piece of code or a repository from showing that an AI produced it. To install it, see `INSTALL.md` at the root of the repository.

## While writing

As soon as Claude writes a file, it follows the matching page of `reference` (prose, code, interface, documents and images, git), then runs the scan on what it wrote. The core of the six bans and rule zero (the work comes before the form) are at the top of `SKILL.md`. Before handing back, it also rereads its text as a stranger hunting for its own tics, and rewrites every sentence that came out in its usual shape: `reference/models.md` lists the known tics of the Claude models (Opus, Sonnet, Haiku, up to 5.5) and of Qwen (the 3 family, including 3.6 and 3.8).

## /strip-ai-traces

Type `/strip-ai-traces` followed by a file, a folder or a repository. The scan lists each trace with its line. What is safe to change (curly quotes, invisible characters, non-breaking spaces, rules between sections) is fixed by the script with `--fix`. The rest is fixed by hand (em dash, emoji, Title Case, typical phrasing, chatbot leftovers) or asked of you (commit already pushed, tool file tracked by git, branch named after a tool).

Strings in code, translation files, data and code blocks do not change: they are values.

## Git history

On the first git command in a repository, Claude runs `history.py`, unless the commits go through clean-commits, which checks and cleans the same commits. The unpushed commits of the current branch lose their signature lines, the author stays. Commits already pushed are never rewritten: Claude gives their number, their ids and the commands for you to run yourself. A co-author who is a person stays, even if their name is Claude.

## What is never removed

The provenance of a generated image (C2PA, IPTC, Stable Diffusion or ComfyUI data, SynthID): Claude says it is there.

## The folder

`SKILL.md` holds the procedure, `reference` the lists and the rules, `scripts` the scan (`scan.py`) and the history (`history.py`), `tests` the patterns, `commands` the command.
