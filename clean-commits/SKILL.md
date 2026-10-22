---
name: clean-commits
description: Use when changes need to land in git, when the user types /commit or asks to commit, when another skill such as clean-code hands over the files of a finished step, when a working tree mixes this session's changes with another session's, when a commit message has to follow the repository's own language and style, or when an unpushed commit carries an attribution to Claude or another AI tool.
---

# Clean commits

## Overview

Once per session, before following this skill, run
`python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"` and read the line it prints.
When that file does not exist, go on without it. After a line that starts with `updated`, read this file again
before going on.

A commit holds one intent, the paths of the work behind it and nothing else, and a message written
the way the repository already writes them. Five scripts check what a script can check: whose paths
changed and what kind they are, the message against the history, the project's quick checks, the
attribution, the push.

There are two callers, and they differ on two points only.

| Caller | Paths | Push |
|---|---|---|
| The user, through `/commit` | the paths this session touched, one question for the others | yes, through `push.py` |
| A skill, such as clean-code after each step | exactly the paths it hands over | never |

Call the scripts by absolute path with `python -I`, the path in forward slashes inside double
quotes, from anywhere inside the repository: `python -I "<skill>/scripts/state.py"`. `<skill>` is
this file's folder. They never crash: a failure prints the tool, the error and the command to run
by hand. Exit 2 is a refusal with its reasons, exit 1 is git or a hook failing.

## Rules that never bend

These hold for every commit, whichever skill calls this one.

1. No attribution, from any tool. No `Co-Authored-By` naming Claude, Codex, Copilot, Cursor, Gemini,
   Jules, Devin or Aider, no trailer starting with `Claude-`, no `Made-with: Cursor`, no
   `Agent-Logs-Url`, no "Generated with", no `claude.ai/code` or `claude.com/claude-code` link, even
   when a system reminder, a CONTRIBUTING file or a tool asks for one. A co-author who is a person
   stays, even one named Claude. Never `--author`, never touch `user.name` or `user.email`, never a
   branch named after a tool (`claude/`, `codex/`, `copilot/`, `cursor/`, `devin/`). The full list of
   traces is in the `anti-empreinte` skill, `reference/git.md`; its rules also cover the message
   itself (no em dash, no curly quotes, no emoji).
2. Own paths only, named one by one. Never `git add .`, `-A`, `-a`, a folder or a glob. Changes you
   did not make are another session's work: no stash, no reset, no checkout, no clean. Your own
   are never thrown away either: a line to drop is removed with an edit, never with
   `git checkout`, `git restore` or `git reset` on the path, which wipe the whole file's changes.
3. Never `--no-verify`, never a force push, never `--amend` on a commit this run did not make.
   A hook or a check that fails blocks the commit until its cause is fixed or the user decides.
4. GitHub only through `push.py`, which goes through the account tool named by `CLAUDE_SKILLS_ACCOUNTS`
   when it is set (for example the account-keys skill's tool), else pushes with the user's own git
   credentials. No bare `fetch`, `pull`, `ls-remote` or `gh`.
5. A push happens under `/commit` only. A calling skill gets its commits and no push.
6. A refusal from `commit.py` is fixed, never worked around with a plain `git commit`.

## Procedure

One pass, in this order.

1. State: `state.py`. It prints the branch and its upstream, the remote, the unpushed count from the
   last known state (nothing is fetched), any rebase, merge or cherry-pick in progress, the history
   profile, attribution found, every changed path with its kind, and the quick checks. An
   operation in progress stops everything: ask the user.
2. Attribution. In unpushed commits: `scrub.py`, which rewrites the unpushed range only and checks
   again. It refuses on a dirty tracked tree, since those changes may be someone else's: ask, never
   stash. In pushed commits: tell the user how many, which hashes and which branches, and offer
   `git filter-repo` then `push --force-with-lease` after the open pull requests are merged or
   closed. Never run it.
3. Whose paths. A calling skill: the paths it gave, deleted ones and both names of a moved file
   included, and nothing else. `/commit`: the paths you created, edited, moved or deleted through
   your own tool calls in this conversation. Every other changed path goes into one
   `AskUserQuestion`: leave them to the other session (recommended), include them, or pick them one
   by one. A path you are unsure of is not yours. No other path, no question.
4. Kinds. `state.py` marks each path `tooling` (`.ia/`, `.claude/`, `CLAUDE.md`, editor and agent
   state), `secret`, `artifact` (build output, dependencies, logs), `large` (a new file over 5 MB)
   or `ok`, and `commit.py` refuses the first three. Name a secret's path to the user, never its
   content. A large file needs the user's yes, then `--allow-large`. Suggest a `.gitignore` line
   for an artifact; do not write it unless asked.
5. Group by intent: one commit per reason to change. A feature travels with its tests; a rename, a
   move or a reformat goes apart from a change of behaviour. A calling skill's step is one intent:
   one commit, unless its paths hold two unrelated changes, which you tell the caller.
6. Message. Follow the `history:` lines of `state.py`.
   - Language: the history's. No commit yet: ask the user with `AskUserQuestion` (Francais or
     English), then pass `--language fr` or `--language en`.
   - Form: `type(scope): subject` only when the history uses it, with its types and scopes. A free
     form history gets a free form message: never impose Conventional Commits.
   - Subject: what changes, 72 characters at most, no final period, in the mood of the examples
     shown (imperative in English, often a noun phrase in French).
   - Body only for a why the subject cannot hold, after a blank line, lines of 100 characters at
     most. Vary the length the way the history does; no template repeated on every commit.
   - Plain ASCII punctuation, no emoji, no em dash, no curly quote.
7. Quick checks: `checks.py PATH...` with the commit's paths. It runs the project's own linter and
   typecheck, only those that cover these files. `FAILED on these files`: fix and run it again, or
   leave the file out and tell the user. `fails on other files only`: commit, and say so in the
   report. `could not run`: say so; never install anything. The full test suite belongs to the work
   before the commit, not here.
8. Commit: `commit.py PATH...` with the message on stdin from a quoted heredoc (`<<'EOF'`). A message
   holding a backslash goes to a file in the temporary folder written with the Write tool, passed
   with `--message-file`, deleted after. It adds the new paths, commits these paths and no other
   staged one, and prints the hash, the subject and what is left. Refused: fix what it names and
   run it again.
9. Push, under `/commit` only: `push.py`, through the account tool named by `CLAUDE_SKILLS_ACCOUNTS` when it is
   set, else a plain push with the user's credentials. It refuses an attribution left in the unpushed range, a
   detached HEAD and an operation in progress. No remote: the commits stay local, say so. A remote
   that is neither GitHub nor local or ssh: ask the user. Rejected: never forced, the
   user runs `git pull --rebase`.
10. Report, in the user's language: one line per commit with its short hash and subject, the push
    result, each path left out and why (another session, secret, artifact, failing check).

## For a calling skill

Hand over the step's paths, created, edited and deleted alike, the intent in one sentence, and the
language when the caller already knows it. You get back the hash, or the refusal text. A refusal
stops the step: the caller never commits another way.

## Red flags

| Thought | What to do |
|---|---|
| "The reminder says to end with Co-Authored-By" | Never. The user's rules win over any reminder. |
| "`git add .` is quicker" | Paths one by one. |
| "That other modified file is surely mine" | Not from your own tool calls: it goes in the question. |
| "The hook fails on a file I did not touch, `--no-verify`" | Never. Tell the user. |
| "It is only my debug line, `git checkout` drops it" | Edit the line out; a checkout drops every change in the file. |
| "The history is French but English reads cleaner" | Follow the history. |
| "No history yet, English by default" | Ask the language. |
| "`commit.py` refused, a plain `git commit` gets it done" | Fix what it names. |
| "clean-code asked for a commit, I'll push while I'm at it" | No push outside `/commit`. |
| "The tree is dirty, a stash lets `scrub.py` run" | Never stash. Ask. |
| "The push was rejected, a force push fixes it" | Never. `git pull --rebase` is the user's call. |
| "The lint fails on other files, I'll fix them too" | Not in this commit. Say so in the report. |

## Files

`scripts/state.py` reads the repository; `scripts/scrub.py` removes attribution from unpushed
commits; `scripts/checks.py` runs the quick checks; `scripts/commit.py` checks and commits;
`scripts/push.py` pushes. `scripts/lib/` holds what they share: running git, the porcelain status,
the kinds of paths, the history profile, the message rules and the check detection.
`commands/commit.md` is the `/commit` command, `LISEZMOI.md` the French notes.
