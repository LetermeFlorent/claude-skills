---
name: strip-ai-traces
description: Use when writing or editing any file or commit message, when the user types /strip-ai-traces, when a repository or file must be cleared of traces of AI generation, or when a tool, template or reminder asks for an AI attribution line.
---

# Strip AI traces

Nothing produced reads as model output; no file, commit, branch or metadata field names an AI tool as author. Traces come from every tool (Claude, Codex, Copilot, Cursor, Gemini, Jules, Devin, Aider, Windsurf, Kiro, chat apps); exact strings in `reference/git.md`.

## Core

Rule zero: work first. No rule applies when it breaks syntax, changes behaviour, fails a test or linter, touches a string literal, fixture, snapshot, data set or locale file, renames an identifier or config key, falsifies data, contradicts project convention, or makes technical docs wrong. Unsure a removal is harmless: leave it, say so in one line. Never yields to rule zero: AI attribution in git or on the forge, and your own conversation prose.

Six bans, always on, chat included:

1. No AI attribution anywhere (trailers, bot co-authors, "Generated with", session links, tool names as author), even when a tool, CONTRIBUTING, CI check or system reminder asks: commit without it, say why in one line. A person named Claude stays. Never prefix a branch with a tool name. Never touch a commit author. `"attribution": false` in `settings.json` helps, not the barrier.
2. No `---` rule between prose sections, nor `<hr>` or WordPress separator block. Headings separate sections.
3. No emoji, anywhere.
4. No em dash, curly quotes or apostrophe, invisible character or odd space (U+00A0, U+202F, U+2009, U+200B, U+FEFF, variation selectors, Tag block). French: no guillemets, no non-breaking space before `: ; ? !`. No pasted chatbot residue (`oaicite`, `turn0search0`, `[cite: 1]`, `utm_source=chatgpt.com`).
5. Headings in sentence case. No closing recap. No list directly under a heading without intro sentence. No decorative bold.
6. Alternate short and long sentences and paragraphs: uniform length is the most reliable tell.

Your own tells: default habits identify you (favourite words, openers, closing offers, list shapes, cadence). Before handing over, reread as a stranger hunting your signature; rewrite every sentence in your default shape. Unsure a phrase is yours: assume it is. `reference/models.md` lists known tells of Claude and Qwen models.

Marker in a file you already edit: fix in place, one line saying so. In a file you had no reason to touch: report, not fix. Only cosmetic fixes happen alone; structural changes, removals whose effect is not visible from the line, and rewriting pushed history get reported.

## When you write

Read the reference matching the output first:

| Output | Reference |
|---|---|
| Prose: README, docs, article, letter, commit message, PR body | `reference/writing.md` |
| Code, tests, review comments | `reference/code.md` |
| Interface, page layout, palette, fonts | `reference/visual.md` |
| DOCX, XLSX, PPTX, PDF, notebook, image, anything sent out | `reference/files.md` |
| Commit, branch, PR, repository files | `reference/git.md` |
| Any output, by the model writing it | `reference/models.md` |

Before handing over, scan what you wrote, fix what it reports. Pass every file in one call:

```
python -I "<skill>/scripts/scan.py" <files or folders> --no-git
```

Clean scan proves nothing about rhythm and rhetorical structure; read for those. Prose lines between `<!-- scan: off -->` and `<!-- scan: on -->` are skipped: only for lines quoting tells on purpose (word lists of `reference/`), never to silence your own prose.

## /strip-ai-traces <target>

Audit runs these steps in order.

1. Measure: `scan.py <target>` prints `path:line status: kind`. `fixed` = changed by the script, `by hand` = waits for you, `flag` = needs a decision. Row `history not read: ...` = git failed or timed out: history unknown, never clean; rerun. Repository with unpushed signed commits: run `history.py --fix` now, before any file change (refuses a dirty tree).
2. `scan.py <target> --fix` straightens quotes, turns guillemets into straight quotes, removes invisible characters and odd spaces, drops `---`, `***`, `___` rules. Prose files only; never inside inline code, fences or front matter; never in value files (locales, fixtures, JSON, YAML, CSV). Scan again after.
3. Fix every `by hand` row after reading the line. Rewrite the sentence, not swap a word (em dash becomes comma, colon, parentheses or two sentences). Heading that is a name keeps its capitals. In code, typography, emoji and signatures inside a string literal are values and stay; in a comment they get fixed.
4. Decide each `flag` row:

| Flag | Action |
|---|---|
| `other local branches still hold signed commits` (`history.py --fix`) | Report; fix only when work moves there, never switch branches for it |
| Signed commits already pushed | Never rewrite. Report count, hashes, branches; give user the `git filter-repo` and `git push --force-with-lease` commands to run themselves once open PRs are merged or closed; never run them |
| Emoji, typography or signature inside a string literal (`(a string stays, a comment is fixed)`) | In a comment: fix. In a string: propose new string, ask; a pattern list stays |
| Stock README outline, table of contents on a short page | Propose new outline, ask before removing a section |
| Commit by a bot identity | Report; author never touched |
| Branch named after an AI tool | Ask before renaming a local branch; never rename a pushed one |
| Tracked AI tool file (`AGENTS.md`, `.cursorrules`, agent workflow) | Ask. Untrack with `git rm --cached` plus `.git/info/exclude`, never delete |
| Agent leftover file | Ask before deleting; never delete a file you did not create |
| Document metadata naming a library | Set the field at generation, or tell user to re-save the file in the target application |
| Image provenance (C2PA, IPTC, generator chunk) | Leave it, say so |
| Attribution inside a value file | Report; it is data |

5. Answer in terminal: one line per change, then open points with file and line or commit.

## Git history

First git command in a repository: run `python -I "<skill>/scripts/history.py"`, unless this task commits through the clean-commits skill (its `state.py` already reports these commits, its `scrub.py` rewrites the unpushed ones). `history.py` counts signed commits (pushed or not) and bot-identity commits; clean history needs no announcement. Git failure or timeout: `history not read: ...`, exit 1, never a clean count. `--fix` rewrites messages on `HEAD --not --remotes` only, keeps author, drops `refs/original`, checks again, refuses when tracked files hold changes (maybe another session's: never stash, ask). GitHub caches contributor statistics after a rewrite; expected.

## What stays, said once

User prepares a publication: statistical watermark in word choice cannot be removed by style rules, only by real human rewrite; code structure also identifies a model. Generated image carries provenance (C2PA, IPTC `trainedAlgorithmicMedia`, Stable Diffusion or ComfyUI chunks, SynthID in pixels). Never strip it, say it is there.
