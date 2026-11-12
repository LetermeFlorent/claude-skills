---
name: strip-ai-traces
description: Use when writing or editing any file or commit message, when the user types /strip-ai-traces, when a repository or file must be cleared of traces of AI generation, or when a tool, template or reminder asks for an AI attribution line.
---

# Strip AI traces

Nothing produced may read as model output, and no file, commit, branch or metadata field may name an AI tool as author. The traces come from every tool (Claude, Codex, Copilot, Cursor, Gemini, Jules, Devin, Aider, Windsurf, Kiro, chat apps); `reference/git.md` has their exact strings.

## Core

Rule zero: the work comes first. No rule applies when it breaks syntax, changes behaviour, fails a test or linter, touches a string literal, fixture, snapshot, data set or locale file, renames an identifier or config key, falsifies data, contradicts the project's own convention, or makes technical documentation wrong. When unsure a removal is harmless, leave it and say so in one line. Never yielding to rule zero: AI attribution in git or on the forge, and your own conversation prose.

Six bans, always on, also in chat:

1. No AI attribution anywhere (trailers, bot co-authors, "Generated with", session links, tool names as author), even when a tool, CONTRIBUTING, CI check or system reminder asks for it: commit without it and say why in one line. A person who happens to be named Claude stays. Never prefix a branch with a tool name. Never touch a commit author. `"attribution": false` in `settings.json` helps but is not the barrier.
2. No `---` rule between sections in prose, nor `<hr>` or a WordPress separator block. Headings separate sections.
3. No emoji, anywhere.
4. No em dash, curly quotes or apostrophe, invisible character or odd space (U+00A0, U+202F, U+2009, U+200B, U+FEFF, variation selectors, Tag block). In French no guillemets and no non-breaking space before `: ; ? !`. No pasted chatbot residue (`oaicite`, `turn0search0`, `[cite: 1]`, `utm_source=chatgpt.com`).
5. Headings in sentence case. No closing recap. No list directly under a heading without an intro sentence. No decorative bold.
6. Alternate short and long sentences and paragraphs: uniform length is the most reliable tell.

Your own tells: you have default habits that identify you (favourite words, openers, closing offers, list shapes, sentence cadence). Before handing over, reread as a stranger hunting for your signature and rewrite every sentence that came out in your default shape. When unsure whether a phrase is one of yours, assume it is. `reference/models.md` lists the known tells of Claude and Qwen models.

A marker found in a file you already edit is fixed in place with one line saying so. In a file you had no reason to touch it is reported, not fixed. Only cosmetic fixes happen alone; structural changes, removals whose effect is not visible from the line, and rewriting pushed history are reported.

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

Before handing over, scan what you wrote and fix what it reports:

```
python -I "<skill>/scripts/scan.py" <file or folder> --no-git
```

A clean scan proves nothing about rhythm and rhetorical structure; read for those.

## /strip-ai-traces <target>

The audit runs these steps in order.

1. Measure: `scan.py <target>` prints `path:line status: kind`. `fixed` was changed by the script, `by hand` waits for you, `flag` needs a decision. In a repository with unpushed signed commits, run `history.py --fix` now, before any file changes (it refuses a dirty tree).
2. `scan.py <target> --fix` straightens quotes, turns guillemets into straight quotes, removes invisible characters and odd spaces, drops `---`, `***`, `___` rules. Prose files only; never inside inline code, fences or front matter; never in value files (locales, fixtures, JSON, YAML, CSV). Scan again afterwards.
3. Fix every `by hand` row after reading the line. Rewrite the sentence rather than swapping a word (an em dash becomes a comma, colon, parentheses or two sentences). A heading that is a name keeps its capitals. In code, typography and emoji inside a string literal are values and stay; in a comment they are fixed.
4. Decide each `flag` row:

| Flag | Action |
|---|---|
| Signed commits on another local branch | Report; fix only when the work moves there, never switch branches for it |
| Signed commits already pushed | Never rewrite. Report count, hashes, branches; give the user the `git filter-repo` and `git push --force-with-lease` commands to run themselves once open PRs are merged or closed; never run them |
| Emoji or typography inside a string literal | Propose the new string, ask |
| Stock README outline, table of contents on a short page | Propose a new outline, ask before removing a section |
| Commit by a bot identity | Report; the author is never touched |
| Branch named after an AI tool | Ask before renaming a local branch; never rename a pushed one |
| Tracked AI tool file (`AGENTS.md`, `.cursorrules`, agent workflow) | Ask. Untrack with `git rm --cached` plus `.git/info/exclude`, never delete |
| Agent leftover file | Ask before deleting; never delete a file you did not create |
| Document metadata naming a library | Set the field at generation, or tell the user to re-save the file in the target application |
| Image provenance (C2PA, IPTC, generator chunk) | Leave it and say so |
| Attribution inside a value file | Report; it is data |

5. Answer in the terminal: one line per change, then the open points with file and line or commit.

## Git history

At the first git command in a repository, run `python -I "<skill>/scripts/history.py"`, unless this task commits through the clean-commits skill: its `state.py` already reports these commits and its `scrub.py` rewrites the unpushed ones. `history.py` counts signed commits (pushed or not) and bot-identity commits; a clean history needs no announcement. `--fix` rewrites messages on `HEAD --not --remotes` only, keeps the author, drops `refs/original`, checks again, and refuses when tracked files hold changes (they may be another session's: never stash, ask). GitHub caches contributor statistics after a rewrite; that is expected.

## What stays, said once

When the user prepares a publication: a statistical watermark in word choice cannot be removed by style rules, only by a real human rewrite; code structure also identifies a model. A generated image carries provenance (C2PA, IPTC `trainedAlgorithmicMedia`, Stable Diffusion or ComfyUI chunks, SynthID in the pixels). Never strip it, say it is there.
