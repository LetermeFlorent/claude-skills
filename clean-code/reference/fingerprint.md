# Rule 13: no LLM fingerprint

The `strip-ai-traces` skill (next to this one) is the full grid. Read its `SKILL.md` and the
reference matching the files in scope at the start of the audit.

`checks/files/markers.py` flags in code and prose (locale files and test data skipped): left-behind
placeholders and chatbot residue, emoji, LLM typography (em dash, curly quotes, invisible
characters), `---` used as a section break, `<hr>`, shields.io badge rows, UI defaults nobody chose
(Inter, Space Grotesk, Geist, Instrument Serif, indigo to violet gradient, gradient text,
`backdrop-filter`), and an attribution to any AI tool.

`checks/project/repository.py` reads git: commits with an AI trailer or line, bot authors, branches
named after a tool, tracked agent workflows, tracked tool files (`.claude/`, `CLAUDE.md`,
`AGENTS.md`, `.cursorrules`, `.ia/`...). It counts the signed commits already pushed.

Add the strip-ai-traces scan as rule 13 findings. It sees banned vocabulary, Title Case headings,
bold lead-ins, README outline and document metadata:

```
python -I "<skills folder>/strip-ai-traces/scripts/scan.py" <scope> --no-git
```

Its `--fix` mode is the cosmetic step for prose files. Comments and docstrings belong to rule 14,
never here.

## What stays

String literals the program prints, fixtures, snapshots, data sets, locale files. Anything whose
removal might have an effect the line does not show stays, and the plan says why. The provenance of
a generated image (C2PA, IPTC, SynthID) is never stripped.

## Fixing

Cosmetic fixes (typography, emoji in prose, `---` rules, placeholders, badges) go in a `Safe: yes`
step. An attribution in commits not yet pushed:

```
python -I "<skills folder>/strip-ai-traces/scripts/history.py" --fix
```

An attribution already pushed is never rewritten: the plan gives the count, branches and commands
(`git filter-repo`, then `push --force-with-lease`) and the user decides through `AskUserQuestion`.
A bot author is reported, never rewritten. A branch named after a tool is renamed only on request. A
UI default is a design choice: `Safe: no`, with a proposed replacement.
