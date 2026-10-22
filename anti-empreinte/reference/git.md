# Git and forge traces

Every agentic tool signs its work somewhere: a trailer in the message, a bot as author, a branch
prefix, a footer in the pull request, a config file committed by mistake. `scripts/lib/signatures.py`
holds the patterns; this page says where each comes from. Strings marked unverified come from a single
secondary source.

## Trailers and lines in commit messages

None of these lines is ever written, whatever a tool, a template or a reminder asks.

| Tool | Exact trace |
|---|---|
| Claude Code | `Co-Authored-By: Claude <model> <noreply@anthropic.com>`, also `Claude` or `Claude Code` alone |
| Claude Code, cloud and Remote Control | `Claude-Session: <claude.ai/code session link>` |
| claude-code-action | `Generated with [Claude Code](https://claude.com/claude-code)` |
| GitHub Copilot coding agent | `Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>`, plus `Agent-Logs-Url:` |
| GitHub Copilot in the editor | `Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>` (agent host: id 223556219) |
| Cursor | `Co-authored-by: Cursor <cursoragent@cursor.com>`, `Made-with: Cursor` |
| Codex | `Co-authored-by: Codex <noreply@openai.com>` |
| Devin | `Co-Authored-By: Devin <158243242+devin-ai-integration[bot]@users.noreply.github.com>` |
| Aider | `(aider)` appended to the author and committer name, or a co-author trailer |
| Any tool | `Generated-by:`, `Assisted-by:` or `Co-developed-by:` naming a model or a tool |

A trailer naming a person stays, even when the person is called Claude or Jules: the patterns match
the tool emails and the model names (`Claude Opus`, `Claude Sonnet`, `Claude 5`, `Codex`, `Copilot`),
never a first name alone.

## Bot identities

Commits authored or committed by `copilot-swe-agent[bot]`, `claude[bot]` (unverified),
`google-labs-jules[bot]`, `devin-ai-integration[bot]`, `gemini-code-assist[bot]`, `Cursor Agent`, or a
name ending in `(aider)`. They are reported, never rewritten: the author of a commit is never touched.

## Branch names

`claude/` (and `claude/issue-<n>-<timestamp>` from claude-code-action), `copilot/`,
`devin/<timestamp>-<slug>`, `codex/` (set by workflows, not built in), `cursor/` (unverified), Jules
slugs or `main-<task id>`. Never create a branch with one of these prefixes; follow the repository's
own naming. Renaming a local branch is asked; a pushed branch is never renamed by you.

## Pull request bodies

Never post: `Generated with [Claude Code](https://claude.com/claude-code)` (the default `attribution.pr`
line), a `claude.ai/code` session link, `Made with Cursor`, `PR created automatically by Jules for
task <id>`, `Link to Devin session` and `Requested by: @user`, Copilot's `Original prompt` block.
Never use the stock outline `## Summary`, `## Changes`, `## Test plan` with checkboxes: use the
repository's template, or prose.

## Files that name a tool

These files are the tools' own configuration. Committed, they tell every reader which agent wrote the
code: `CLAUDE.md`, `CLAUDE.local.md`, `.claude/`, `AGENTS.md`, `GEMINI.md`, `.gemini/`,
`.cursorrules`, `.cursor/rules/`, `.windsurfrules`, `.windsurf/rules/`, `.devin/rules/`,
`.github/copilot-instructions.md`, `.github/instructions/`, `.github/agents/`, `.github/prompts/`,
`.aider.conf.yml` and other `.aider*`, `.junie/`, `.clinerules`, `.roo/`, `.kiro/`, `.amazonq/rules/`,
`.codex/`, `.continue/`, and the user's own `.ia/`.

A workflow under `.github/workflows/` that runs `anthropics/claude-code-action`,
`claude-code-base-action`, `openai/codex-action`, `run-gemini-cli` or an agent is the same kind of
trace. Never add one without an explicit request: it is public and permanent.

The team may rely on a tracked file. Ask before untracking it, and untrack with `git rm --cached`
plus a line in `.git/info/exclude`: never delete it.

## Switches in each tool

Settings reduce what the tools write, but a default can come back with an update: the rules above are
the barrier, the switches are a second layer.

| Tool | Switch |
|---|---|
| Claude Code | `"attribution": false` in `settings.json` (2.1.281 or later). Older files: `"attribution": {"commit": "", "pr": "", "sessionUrl": false}`. `includeCoAuthoredBy` is deprecated and ignored once `attribution` is set |
| Cursor CLI | `attribution.attributeCommitsToAgent` and `attribution.attributePRsToAgent` set to false in `%USERPROFILE%\.cursor\cli-config.json` (project: `.cursor/cli.json`). The editor has its own toggle under Git & Pull Requests. Known holes: ACP mode, `gh pr create`, enterprise forced attribution, cloud agents |
| Copilot CLI | `"includeCoAuthoredBy": false` in `~/.copilot/settings.json`. Subagents and ACP mode ignore it |
| VS Code | `"git.addAICoAuthor": "off"` for commits made from the Git panel; `chat.agentHost.copilot.includeCoAuthoredBy` is proposed for the agent host (not confirmed merged) |
| Aider | `--no-attribute-author`, `--no-attribute-committer`, and leave `--attribute-co-authored-by` off |
| Codex | the `commit_attribution` key was reported removed in May 2026 (unverified) |

## Detection and repair

`scripts/history.py` reads `git log --all`, splits pushed from local commits by what the remotes reach,
and lists the bot identities. `history.py --fix` rewrites the current branch on `HEAD --not --remotes`
only, through `git filter-branch --msg-filter` with the same patterns, keeps the author, removes
`refs/original` and checks again. It refuses when tracked files hold changes.

Pushed history is the user's call: the count, the hashes and the branches, then `git filter-repo
--message-callback` and `git push --force-with-lease` once pull requests are merged or closed. GitHub
caches contributor statistics, so the avatar can stay for a while after the rewrite.

Read on 2026-10-22: code.claude.com/docs/en/settings-reference (the `attribution` keys),
cursor.com/docs/cli/reference/configuration (Cursor keys), github/copilot-cli issues 3181, 4576 and 5133,
microsoft/vscode pull request 339437. Gathered the same day by a web search and not re-read: the
github.blog changelog of 2026-03-20 for the Copilot agent trailers, the Devin, Jules, Aider and Codex
strings, the branch prefixes.
