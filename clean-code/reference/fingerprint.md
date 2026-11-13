# Rule 13: no LLM fingerprint

`strip-ai-traces` skill (next to this one) holds full grid.

`checks/files/markers.py` flags in code and prose (locale files and test data skipped): left-behind
placeholders and chatbot residue, emoji, LLM typography (em dash, curly quotes, invisible
characters), `---` used as section break, `<hr>`, shields.io badge rows, UI defaults nobody chose
(Inter, Space Grotesk, Geist, Instrument Serif, indigo to violet gradient, gradient text,
`backdrop-filter`), attribution to any AI tool. One finding per file, at its first hit.

`checks/project/repository.py` reads git: commits with AI trailer or line, bot authors, branches
named after a tool, tracked agent workflows, tracked tool files (`.claude/`, `CLAUDE.md`,
`AGENTS.md`, `.cursorrules`, `.ia/`...). Counts signed commits already pushed.

Audit step 3 runs strip-ai-traces scan; it also sees banned vocabulary, Title Case headings, bold
lead-ins, README outline and document metadata. Its `--fix` mode = cosmetic step for prose files.
Comments and docstrings belong to rule 14, never here.

## What stays

String literals program prints, fixtures, snapshots, data sets, locale files. Anything whose removal
might have effect line does not show stays, plan says why. Provenance of generated image (C2PA,
IPTC, SynthID) never stripped.

## Fixing

Cosmetic fixes (typography, emoji in prose, `---` rules, placeholders, badges) go in `Safe: yes`
step. Attribution in commits not yet pushed:

```
python -I "<skill>/../strip-ai-traces/scripts/history.py" --fix
```

Attribution already pushed never rewritten: plan gives count, branches and commands
(`git filter-repo`, then `push --force-with-lease`) for user to run themselves; never run here. Bot
author reported, never rewritten. Branch named after a tool renamed only on request. UI default =
design choice: `Safe: no`, with proposed replacement.
