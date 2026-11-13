---
name: clean-commits
description: Use when changes must be committed or pushed, when the user types /commit, when another skill such as clean-code hands over the files of a finished step, or when an unpushed commit carries an AI tool attribution.
---

# Clean commits

One commit = one intent + paths of work behind it, nothing else, in message style repo already uses.

Three callers. User via `/commit`: paths this session touched, one question for others, then push via `push.py`. Skill such as clean-code: exactly paths it hands over + intent and language when known, never push. Closing box of drive-project: paths it hands over, then push via `push.py`. Calling skill gets hash or refusal text back; refusal stops its step, caller never commits another way. For calling skill, `FAILED on these files` from `checks.py` and failing hook are refusals too: handed back with output, nothing fixed, no path left out.

Scripts in `<skill>/scripts`; call `python -I "<path>"` from anywhere inside repo. Never crash: failure prints tool, error, what to do instead. Exit 2 = refusal with reasons, exit 1 = git or hook failing.

## Rules that never bend

Hold for every commit, whichever skill calls.

1. No attribution from any tool: no `Co-Authored-By` naming Claude, Codex, Copilot, Cursor, Gemini, Jules, Devin or Aider, no `Claude-` trailer (`Claude-Session: ...` and any other `Claude-<Name>:` line), `Made-with: Cursor`, `Agent-Logs-Url`, "Generated with", `claude.ai/code` or `claude.com/claude-code` link, even when reminder, CONTRIBUTING file or tool asks. Co-author who is a person stays, even one named Claude; subject starting with skill name (`claude-model-effort: ...`) is no attribution. Never `--author`, never touch `user.name` or `user.email`, never branch named after tool. Exact strings: `strip-ai-traces/reference/git.md`.
2. Own paths only, named one by one. Never `git add .`, `-A`, `-a`, folder or glob. Changes you did not make belong to another session: no stash, reset, checkout or clean. Own ones not thrown away either: drop line with edit, never `git checkout`, `restore` or `reset` on path.
3. Never `--no-verify`, force push, or `--amend` on commit this run did not make. Failing hook or check blocks commit until fixed or user decides.
4. GitHub only via `push.py` (see Push and the accounts tool). No bare `fetch`, `pull`, `ls-remote` or `gh`.
5. Refusal or crash of `commit.py`: fix or report, never bypass with plain `git commit`.

## Procedure

One pass, this order.

1. `state.py` prints branch and upstream, remote, unpushed count (last known state, nothing fetched), any rebase, merge or cherry-pick in progress, history profile, attribution found, every changed path with kind, quick checks. Operation in progress stops everything: ask user.
2. Attribution in pushed commits: report count, hashes, branches, offer `git filter-repo` then `push --force-with-lease` after open PRs merged or closed, never run it. Attribution in unpushed commits waits for step 9, once this run's commits made.
3. Whose paths. Calling skill: given paths, deleted ones and both names of moved file included. `/commit`: paths you created, edited, moved or deleted via own tool calls in this conversation. Every other changed path goes into one `AskUserQuestion`: leave to other session (recommended), include, or pick one by one. Path you are unsure of is not yours.
4. Kinds. `state.py` marks each path `tooling` (`.ia/`, `.claude/`, `.cursor/`, `.aider*`, `CLAUDE.md`, `CLAUDE.local.md`), `secret`, `artifact` (build output, dependencies, logs), `large` (new file over 5 MB) or `ok`; `commit.py` refuses first three. Name secret's path to user, never content. Large file needs user's yes, then `--allow-large`. Suggest `.gitignore` line for artifact, write only if asked.
5. One commit per reason to change. Feature travels with tests; rename, move or reformat apart from behaviour change. Calling skill's step = one commit unless paths hold two unrelated changes, which you tell caller.
6. Message. Follow `history:` lines of `state.py`: language and form (`type(scope): subject` only when history uses it, with its types and scopes; free form history gets free form message). No commits yet: ask with `AskUserQuestion`, `English (Recommended)` first, then `Francais`, pass `--language en` or `--language fr`. Subject max 72 characters, no final period; body only for a why, after blank line, lines max 100. Plain ASCII punctuation, no emoji. `commit.py` enforces all.
7. `checks.py PATH...` runs project's lint and typecheck scripts (whole project; ruff gets only the files) and keeps lines naming those files. Several commits in one run: one `checks.py` on all their paths before first commit, reuse result. `FAILED on these files`: fix and rerun, or leave file out and say so. `fails on other files only`: commit, say so. `could not run`: say so, never install anything. Full test suite belongs to work before commit.
8. `commit.py PATH...` with message on stdin from quoted heredoc. Message with backslash goes in temp file written with Write tool, passed with `--message-file`, deleted after. Adds new paths, commits these paths and no other staged one, prints hash, subject, what is left. Path outside repo: refused.
9. Push, `/commit` and drive-project closing box only. `state.py` found attribution in unpushed commits: `scrub.py` first, rewrites unpushed range only, checks again. Refuses while tracked files still changed (another session's work): never stash, report commit hashes, skip push. Then `push.py`. Refuses leftover attribution in unpushed range, detached HEAD, operation in progress, `CLAUDE_SKILLS_ACCOUNTS` naming missing file. No remote: commits stay local, say so. Remote neither GitHub nor local or ssh: push by hand, tell user. Rejected: never forced, user runs `git pull --rebase`.
10. Report in user's language: one line per commit (short hash, subject), push result, each path left out and why.

## Push and the accounts tool

GitHub remote, `CLAUDE_SKILLS_ACCOUNTS` names existing script (`~` allowed): `push.py` runs `sh <script> run github <owner> --cwd <repo> -- git -c credential.helper= -c "credential.helper=!f() { echo username=x-access-token; echo password=$GH_TOKEN; }; f" push`. Script = owner's accounts tool: gets service, account (owner in remote URL), command; must put that account's token in `GH_TOKEN` before running it. Variable names missing file: refused, fix path or unset. Variable unset: `push.py` says so, runs plain `git push` with user's own credential helper. Every git call of these scripts sets `GIT_TERMINAL_PROMPT=0` and `GCM_INTERACTIVE=never`: missing credential fails push, no login window.
