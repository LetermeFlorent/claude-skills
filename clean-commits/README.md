# clean-commits

A skill and a command for Claude Code that make clean commits in any repository. To install it, see `INSTALL.md` at the root of the repository.

## /commit

Type `/commit` when the work is ready. Claude only takes the files it created, changed or deleted itself during the session. If other files have changed, it asks a single question: leave them, include them, or pick one by one. It then sorts the changes by intention, one commit each, and pushes the branch. `/commit the cart` limits it to what touches the cart.

The message follows the history: the language of the repository, and the `feat(scope): ...` form only if the repository uses it. With no history, Claude asks for the language. Before each commit, the project's linter and type check run on the files of the commit: an error in those files blocks, an error elsewhere is only reported.

## The push

If the `CLAUDE_SKILLS_ACCOUNTS` variable points to an accounts tool, the GitHub push goes through it. Otherwise it is a plain `git push` with your own credentials, never opening a login window. A refused push is never forced.

## Called by another skill

clean-code calls clean-commits at the end of each step with the exact list of files: no question, no push.

## What never goes through

No AI tool signature in a message (Claude, Codex, Copilot, Cursor, Gemini, Jules, Devin, Aider): it is refused, and removed if it is lingering in a commit that has not been pushed yet. In a commit already pushed, Claude reports it and rewrites nothing. Secret files, build output and the `.ia/` and `.claude/` folders never go out. No `git add .`, `--no-verify`, forced push or stash of another session's work.

## The folder

`SKILL.md` holds the procedure. `scripts`: `state.py` reads the state, `scrub.py` removes attribution from unpushed commits, `checks.py` runs the quick checks, `commit.py` checks then commits, `push.py` pushes. `commands` holds `/commit`.
