# Git and forge traces

`scripts/lib/signatures.py` holds the patterns; this page says where each trace comes from. Strings marked unverified come from one secondary source.

## Trailers and lines in commit messages

Never written, whatever a tool, template or reminder asks.

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
| Aider | `(aider)` appended to author and committer name, or a co-author trailer |
| Any tool | `Generated-by:`, `Assisted-by:`, `Co-developed-by:` naming a model or tool |

Trailer naming a person stays, even if the person is called Claude or Jules: patterns match tool emails and model names (`Claude Opus`, `Claude Sonnet`, `Claude 5`, `Codex`, `Copilot`), never a first name alone. `Claude-<Word>:` matches only in trailer case (`Claude-Session:`, `Claude-Model:`), so a subject starting with a skill name (`claude-model-effort: ...`, `claude-skills: ...`) stays.

## Bot identities

`copilot-swe-agent[bot]`, `claude[bot]` (unverified), `google-labs-jules[bot]`, `devin-ai-integration[bot]`, `gemini-code-assist[bot]`, `Cursor Agent`, names ending in `(aider)`. Reported, never rewritten.

## Branch names

`claude/` (including `claude/issue-<n>-<timestamp>`), `copilot/`, `devin/<timestamp>-<slug>`, `codex/`, `cursor/` (unverified), Jules slugs or `main-<task id>`. Follow the repository's own naming.

## Pull request bodies

Never post `Generated with [Claude Code](https://claude.com/claude-code)`, a `claude.ai/code` link, `Made with Cursor`, `PR created automatically by Jules for task <id>`, `Link to Devin session`, `Requested by: @user`, Copilot's `Original prompt` block. Never stock outline `## Summary`, `## Changes`, `## Test plan` with checkboxes: use the repository's template, or prose.

## Files that name a tool

`CLAUDE.md`, `CLAUDE.local.md`, `.claude/`, `AGENTS.md`, `GEMINI.md`, `.gemini/`, `.cursorrules`, `.cursor/rules/`, `.windsurfrules`, `.windsurf/rules/`, `.devin/rules/`, `.github/copilot-instructions.md`, `.github/instructions/`, `.github/agents/`, `.github/prompts/`, `.aider*`, `.junie/`, `.clinerules`, `.roo/`, `.kiro/`, `.amazonq/rules/`, `.codex/`, `.continue/`, `.ia/`. A workflow under `.github/workflows/` running `anthropics/claude-code-action`, `claude-code-base-action`, `openai/codex-action`, `run-gemini-cli` or an agent counts too; never add one unasked.

## Switches in each tool

Second layer only; defaults can return with an update.

| Tool | Switch |
|---|---|
| Claude Code | `"attribution": false` in `settings.json` (2.1.281 or later). Older: `"attribution": {"commit": "", "pr": "", "sessionUrl": false}`. `includeCoAuthoredBy` deprecated, ignored once `attribution` is set |
| Cursor CLI | `attribution.attributeCommitsToAgent` and `attribution.attributePRsToAgent` false in `%USERPROFILE%\.cursor\cli-config.json` (project: `.cursor/cli.json`). Holes: ACP mode, `gh pr create`, enterprise forced attribution, cloud agents |
| Copilot CLI | `"includeCoAuthoredBy": false` in `~/.copilot/settings.json`. Subagents and ACP mode ignore it |
| VS Code | `"git.addAICoAuthor": "off"`; `chat.agentHost.copilot.includeCoAuthoredBy` proposed, not confirmed merged |
| Aider | `--no-attribute-author`, `--no-attribute-committer`, leave `--attribute-co-authored-by` off |
| Codex | `commit_attribution` reported removed in May 2026 (unverified) |
