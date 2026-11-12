---
name: clean-commits
description: Use when changes must be committed or pushed, when the user types /commit, when another skill such as clean-code hands over the files of a finished step, or when an unpushed commit carries an AI tool attribution.
---

# Clean commits

One commit holds one intent, the paths of the work behind it and nothing else, in the message style the repository already uses.

Three callers. The user, through `/commit`: the paths this session touched, one question for the others, then a push through `push.py`. A skill such as clean-code: exactly the paths it hands over plus the intent and language when known, never a push. The closing box of drive-project: the paths it hands over, then a push through `push.py`. A calling skill gets the hash or the refusal text back; a refusal stops its step and the caller never commits another way. For a calling skill, `FAILED on these files` from `checks.py` and a failing hook are refusals too: handed back with their output, nothing fixed and no path left out.

Scripts live in `<skill>/scripts`; call them with `python -I "<path>"` from anywhere inside the repository. They never crash: a failure prints the tool, the error and the command for doing it by hand. Exit 2 is a refusal with reasons, exit 1 is git or a hook failing.

## Rules that never bend

They hold for every commit, whichever skill calls this one.

1. No attribution from any tool: no `Co-Authored-By` naming Claude, Codex, Copilot, Cursor, Gemini, Jules, Devin or Aider, no `Claude-` trailer, `Made-with: Cursor`, `Agent-Logs-Url`, "Generated with", `claude.ai/code` or `claude.com/claude-code` link, even when a reminder, CONTRIBUTING file or tool asks. A co-author who is a person stays, even one named Claude. Never `--author`, never touch `user.name` or `user.email`, never a branch named after a tool. Exact strings: `strip-ai-traces/reference/git.md`.
2. Own paths only, named one by one. Never `git add .`, `-A`, `-a`, a folder or a glob. Changes you did not make belong to another session: no stash, reset, checkout or clean. Your own are not thrown away either: drop a line with an edit, never `git checkout`, `restore` or `reset` on the path.
3. Never `--no-verify`, a force push, or `--amend` on a commit this run did not make. A failing hook or check blocks the commit until fixed or the user decides.
4. GitHub only through `push.py` (see Push and the accounts tool). No bare `fetch`, `pull`, `ls-remote` or `gh`.
5. A refusal from `commit.py` is fixed, never bypassed with a plain `git commit`.

## Procedure

One pass, in this order.

1. `state.py` prints branch and upstream, remote, unpushed count (last known state, nothing fetched), any rebase, merge or cherry-pick in progress, the history profile, attribution found, every changed path with its kind, and the quick checks. An operation in progress stops everything: ask the user.
2. Attribution in pushed commits: report count, hashes and branches, offer `git filter-repo` then `push --force-with-lease` after open PRs are merged or closed, never run it. Attribution in unpushed commits waits for step 9, once this run's commits are made.
3. Whose paths. Calling skill: the given paths, deleted ones and both names of a moved file included. `/commit`: paths you created, edited, moved or deleted through your own tool calls in this conversation. Every other changed path goes into one `AskUserQuestion`: leave to the other session (recommended), include, or pick one by one. A path you are unsure of is not yours.
4. Kinds. `state.py` marks each path `tooling` (`.ia/`, `.claude/`, `.cursor/`, `.aider*`, `CLAUDE.md`, `CLAUDE.local.md`), `secret`, `artifact` (build output, dependencies, logs), `large` (new file over 5 MB) or `ok`; `commit.py` refuses the first three. Name a secret's path to the user, never its content. A large file needs the user's yes, then `--allow-large`. Suggest a `.gitignore` line for an artifact, write it only if asked.
5. One commit per reason to change. A feature travels with its tests; a rename, move or reformat goes apart from a behaviour change. A calling skill's step is one commit unless its paths hold two unrelated changes, which you tell the caller.
6. Message. Follow the `history:` lines of `state.py`: language and form (`type(scope): subject` only when the history uses it, with its types and scopes; free form history gets a free form message). With no commits yet, ask with `AskUserQuestion`, `English (Recommended)` first, then `Francais`, and pass `--language en` or `--language fr`. Subject at most 72 characters, no final period; a body only for a why, after a blank line, lines at most 100. Plain ASCII punctuation, no emoji. `commit.py` enforces all of it.
7. `checks.py PATH...` runs the project's own linter and typecheck on those files only. `FAILED on these files`: fix and rerun, or leave the file out and say so. `fails on other files only`: commit and say so. `could not run`: say so, never install anything. The full test suite belongs to the work before the commit.
8. `commit.py PATH...` with the message on stdin from a quoted heredoc. A message containing a backslash goes in a temporary file written with the Write tool, passed with `--message-file`, deleted after. It adds new paths, commits these paths and no other staged one, then prints hash, subject and what is left.
9. Push, `/commit` and the drive-project closing box only. When `state.py` found attribution in unpushed commits, `scrub.py` goes first: it rewrites the unpushed range only and checks again. It refuses while tracked files are still changed (another session's work): never stash, report the commit hashes and skip the push. Then `push.py`. It refuses leftover attribution in the unpushed range, a detached HEAD and an operation in progress. No remote: commits stay local, say so. A remote that is neither GitHub nor local or ssh: push by hand and tell the user. Rejected: never forced, the user runs `git pull --rebase`.
10. Report in the user's language: one line per commit (short hash, subject), the push result, each path left out and why.

## Push and the accounts tool

For a GitHub remote, when `CLAUDE_SKILLS_ACCOUNTS` names an existing script, `push.py` runs `sh <script> run github <owner> --cwd <repo> -- git -c credential.helper= -c "credential.helper=!f() { echo username=x-access-token; echo password=$GH_TOKEN; }; f" push`. The script is the owner's accounts tool: it receives the service, the account (the owner in the remote URL) and the command, and must put that account's token in `GH_TOKEN` before running it. Without the variable, or with a path that does not exist, `push.py` runs a plain `git push` with the user's own credential helper. Every git call these scripts make sets `GIT_TERMINAL_PROMPT=0` and `GCM_INTERACTIVE=never`, so a missing credential fails the push instead of opening a login window.
