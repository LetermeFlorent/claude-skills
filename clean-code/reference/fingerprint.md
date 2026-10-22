# Rule 13 in detail: no LLM fingerprint

The `anti-empreinte` skill is the grid for this rule. Read its `SKILL.md` and the reference that matches
the files in scope (`writing.md`, `code.md`, `visual.md`, `files.md`, `git.md`) at the start of the
audit instead of trusting memory: the tools change their signatures, and the skill follows them. It
lives next to this one, in the same skills folder.

## What the scripts flag

`checks/files/markers.py` reads code and prose, skipping locale files and test data:

- placeholders left behind: `// ... existing code ...`, `# TODO: implement`, an `# Example usage`
  block, and chatbot residue (`<think>`, `oaicite`, `turn0search0`, `[cite: 1]`,
  `utm_source=chatgpt.com`);
- emoji in code, console output, a README or a log message, string literals included;
- LLM typography in comments, docs and prose: em dash, curly quotes and apostrophe, invisible
  characters (no-break and fixed-width spaces, zero width characters, direction marks, variation
  selectors, the Tag block, the Private Use Area);
- a `---` rule used as a section break in prose, and `<hr>` in pages;
- a row of shields.io badges;
- the UI defaults nobody chose: Inter, Space Grotesk, Geist or Instrument Serif, an indigo to violet
  gradient, `indigo-500`, gradient text, glassmorphism through `backdrop-filter`;
- an attribution to any AI tool written in a file.

`checks/project/repository.py` reads git, for every tool and not only Claude: commits whose message
carries a trailer or a line naming Claude, Codex, Copilot, Cursor, Gemini, Jules, Devin or Aider (a
person named Claude is not matched), commits made by a bot identity, branches named after a tool, a
tracked workflow running an agent, and tracked tool files (`.claude/`, `CLAUDE.md`, `AGENTS.md`,
`.cursorrules`, `.github/copilot-instructions.md`, `.ia/` and the others listed in the anti-empreinte
`git.md`). It says how many signed commits are already pushed.

## What the anti-empreinte scan adds

Run it on the scope as part of the measure, and add its rows as rule 13 findings:

```
python -I "<skills folder>/anti-empreinte/scripts/scan.py" <scope> --no-git
```

It sees what `markers.py` does not: banned words and phrases in English and French, Title Case
headings, bold lead-ins, a list right under a heading, a nested fence closed too short, the stock README
outline, and the metadata of documents, notebooks and images. Its `--fix` mode is the cosmetic step of
the plan for prose files.

Reading adds what a pattern misses: a broad `try` that ends on a print, an import added in case, three
identical cards in a grid, the rhythm of the prose.

Comments and docstrings belong to rule 14, never here: one defect counts once.

## What stays, whatever it holds

A string literal the program prints, a fixture, a snapshot, a data set, a locale file: these are
values, and changing them changes the product. When a removal might have an effect that the line does
not show (an import kept for its side effect, a comment a linter reads), it stays and the plan says
why. The provenance of a generated image (C2PA, IPTC source type, SynthID) is never stripped: the plan
says it is there.

## Fixed alone, or asked

Cosmetic fixes go in a `Sure : oui` step: typography, emoji in prose, `---` rules, placeholders,
example blocks, badges.

An attribution in commits not pushed yet is fixed by the anti-empreinte script, on the current branch
and the local range only, author kept:

```
python -I "<skills folder>/anti-empreinte/scripts/history.py" --fix
```

An attribution already pushed is never rewritten by this skill: the plan leaves it as is, gives the
count, the branches and the commands (`git filter-repo`, then `push --force-with-lease` once open pull
requests are merged or closed), and the user decides through `AskUserQuestion`. A bot identity as
author is reported, never rewritten. A branch named after a tool is renamed only when the user says so.

A UI default (font, palette) is a design choice: the plan proposes a replacement, and the step is
`Sure : non`.
