# Folder format

The skeletons to copy, then the rules for scripts and their tests. The finished models sit in
`<claude-skills>`, the clone of this repository, `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills`: open the
closest one before copying a skeleton, and drop any section the skill does not need.

## Contents

Six parts, in the order a new skill needs them.

- SKILL.md
- LISEZMOI.md
- The command
- A subagent brief
- Scripts
- Unit tests

## SKILL.md

Front matter, then the sections in this order.

````markdown
---
name: <folder-name>
description: Use when <situation>, when <symptom or error text>, when the user types /<commande>, or when <another trigger>.
---

# <Title in sentence case>

## Overview

<What the skill is for and its core rule, in a few sentences. Where the scripts are and how to call them.>

## Rules that never bend

These hold <in which phases>.

1. <A rule, with the workaround it forbids named.>

## Procedure

<One sentence on the order.>

1. <A step, with the exact command when one wrong flag breaks something.>

## Red flags

<One sentence.>

| Thought | Reality |
|---|---|
| "<the excuse, in a subject's words>" | <what to do> |

## Files

<One paragraph naming each file and what it holds.>
````

Read the description alone and ask "should I load this now?". It names situations and symptoms,
never what the skill does step by step, and it is written in the third person, since it lands in the
system prompt. The name is the folder's name: lowercase letters, digits and hyphens, 64 characters at
most, verb-first or a gerund (`condition-based-waiting`, `writing-plans`), never `helper` or `utils`.

## LISEZMOI.md

French with accents, for the user, in the tone of `clean-commits/LISEZMOI.md`: what happens when they
use it, in everyday words, never a translation of `SKILL.md`.

````markdown
# <nom>

<Ce que fait la skill, en deux ou trois phrases. Pour l'installer, voir `INSTALL.md` à la racine du dépôt.>

## /<commande>

<Quand la taper, ce que Claude fait alors, ce que l'argument change.>

## <Avec les autres skills, ou ce qui ne passe jamais>

<Qui l'appelle, qui elle appelle, ce qu'elle refuse.>

## Le contenu du dossier

<Chaque fichier et son rôle.>

## Ce qui a été testé

<Écrit après les essais : le scénario, ce que faisait l'agent sans la skill, ce qu'il a fait avec,
ce qui a été corrigé après un essai, ce qui n'a pas été testé et pourquoi.>
````

Until the runs have happened, the last section does not exist; `check_skill.py --draft` refuses it.
When the user chose to skip the tests, it is replaced by `## Pas encore testé` and one sentence on
what stays unproven.

## The command

`commands/<commande>.md`, French without accents, the file name in lowercase ASCII. Only for a skill
the user starts by hand. Add `Agent` and `SendMessage` to `allowed-tools` when the skill sends
subagents.

````markdown
---
description: <Ce que fait la commande, sans accents.>
argument-hint: "[<ce que l'argument peut etre>]"
allowed-tools: Read,Write,Bash,Grep,Glob,Skill,AskUserQuestion
---

Charger la skill `<name>` avec le tool `Skill` et suivre sa partie Procedure, etape par etape. Si
le tool `Skill` ne la trouve pas, lire directement `$CLAUDE_CONFIG_DIR/skills/<name>/SKILL.md`, ou
`~/.claude/skills/<name>/SKILL.md` quand la variable est vide, et l'appliquer pareil.

Precision donnee : $ARGUMENTS. <Ce qu'elle change, et ce qui se passe quand elle est vide.>

Reponse finale en francais, courte : <ce que contient la reponse>.
````

## A subagent brief

`<role>-brief.md` at the root of the folder: a title, one paragraph on when it is sent and how it is
filled, then the prompt in a fence of five backticks with `text` as its language, so that a fence
inside the prompt cannot close it. Every value to fill is a `<...>`. The prompt ends on a fixed
report block, so several answers can be read side by side. Models: `clean-code/reader-brief.md` and
this skill's `subject-brief.md`.

## Scripts

A script earns its place when it checks something better than reading does: a count, a format, a
parse, a git state, a measure. Each one follows all of these.

1. Python 3, standard library first. A dependency is named in `SKILL.md`; installing it is
   the user's call. No `.sh`, `.js` or `.cjs` unless no Python route exists, and then the report says
   why.
2. Called as `python -I "<skill>/scripts/<tool>.py"`, by absolute path in forward slashes. The
   script sets `sys.dont_write_bytecode = True` before any local import, and adds `scripts/lib/` to
   `sys.path` when shared code lives there: `-I` leaves the script's own folder off the path.
3. Never a crash. A guard around `main` prints the tool, the error and the command to run by hand.
   Exit 2 is a refusal with its reasons, exit 1 a failure of git or of the tool.
4. No comment in code: what a comment would say goes into a name. English identifiers. Values named
   once, never a bare number with no name.
5. Files under 150 lines, functions under 40 lines, 4 parameters at most, lines of 120 characters at
   most, 8 code files per folder at most.
6. A subprocess runs at BelowNormal priority, with a timeout, and for git with
   `GIT_TERMINAL_PROMPT=0` and `GCM_INTERACTIVE=never`, so no login window opens on the user's screen.
   GitHub itself goes through the account-keys skill when it is installed, else with the user's own git
   credentials, never a bare `fetch` or `push`.
7. The output is short lines a model reads: one finding per line, counts at the end. Flags live in
   `--help`, not in `SKILL.md`.
8. Never `python -I $VAR` with a variable that may be empty: Python opens its interactive prompt and
   the Bash call hangs until its timeout.

The guard used across the skills of this repository:

```python
def guard(main, hint):
    sys.stdout.reconfigure(encoding=ENCODING, errors=DECODE_ERRORS)
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(INTERRUPTED)
    except Exception as error:
        print(f"{TOOL}: {type(error).__name__}: {error}")
        print(f"by hand: {hint}")
        sys.exit(FAILED)
```

## Unit tests

`tests/test_pure.py`, with `unittest`, on the pure functions: text in, findings out, no network and
no git. A test that needs files uses `tempfile.TemporaryDirectory`. It runs from the skill folder and
must pass before the skill is handed over:

```text
python -I -m unittest discover -s tests -p "test_*.py"
```

Its head puts the scripts on the path the same way the scripts do:

```python
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS / "lib"))
```

Delete any `__pycache__` the runs left behind; `check_skill.py` refuses a folder that holds one.
