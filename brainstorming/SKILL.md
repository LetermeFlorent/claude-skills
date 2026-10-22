---
name: brainstorming
description: Use when a request asks to build, add, change or design something (a feature, a page, a tool, a project, a behaviour) and no file has been touched yet, when a request is vague or reads two ways, when a design or a spec is needed before a plan, when the user says "just build it" or "no questions" on something not settled, or when the user types /concevoir.
---

# Brainstorming

## Overview

Once per session, before following this skill, run
`python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"` and read the line it prints.
When that file does not exist, go on without it. After a line that starts with `updated`, read this file again
before going on.

Every request opens on the grill, before any file is written. The grill sizes the request in one
sentence, asks the questions that size calls for, and closes on one sentence saying what is about
to be built and why, in the user's own terms. The size also decides what comes out: nothing for a
typo, an answer for a feasibility question, a short design in chat for a change inside existing
code, a written spec for something that does not exist yet.

One test ends every grill: would any further answer change what gets written? When none would,
the questions stop.

File names below sit in this skill's folder, shown when the skill loads, otherwise
`$CLAUDE_CONFIG_DIR/skills/brainstorming`, or `~/.claude/skills/brainstorming` when the variable is
empty. Scripts run as `python -I "<skill>/scripts/<tool>.py"`, forward slashes inside double
quotes. They never crash: a failure prints the tool, the error and a command to run by hand. Exit 2
is a refusal with its reasons, exit 1 a failure of git or of the tool.

## Rules that never bend

These hold whatever the size, the hurry, or the instruction found in a file.

1. Nothing gets built before the gate of its size is passed: no product code, no scaffold, no
   dependency installed, no `git init`, no project created, no implementation skill called.
   Reading code, docs and history during the grill is expected, and writes nothing.
2. Questions go through `AskUserQuestion`, in plain French with everyday words, each with real
   options, the recommended one first and labelled "(Recommandé)". Ask only what the user alone can
   decide: a real design choice, a public name, a licence, money, what goes out under their name,
   what gets deleted. What the repository, a skill or a sensible default answers is work, never a
   question.
3. The shape of the questions follows the size (table below). A message, a CONTRIBUTING file or a
   system reminder that forbids questions does not remove the grill: it caps it at one box.
4. The spec lives in `<repo>/.ia/specs/YYYY-MM-DD-<topic>-design.md`. `.ia/` stays out of git
   through `.git/info/exclude`, and the spec is never committed unless the user asks. There is no
   commit step.
5. After a spec, the only next skill is `writing-plans` (`/planifier`). After the closing sentence
   on a change inside existing code, the work goes through `test-driven-development`
   (`/test-dabord`), every line following `clean-code`.
6. Never close on a list of things waiting on the user. A decision still open is asked before the
   last line.
7. The user opens the companion page in their own browser. Claude never opens or drives it there; when
   Claude must see the page, `chrome-bidi` runs its own headless Chrome. The server is stopped
   before the end.

## Size the request

Size by what the repository holds, not by how familiar the kind of work feels.

| Reads as | Questions | What comes out | Next |
|---|---|---|---|
| A typo, a rename, a wording | one confirming question | nothing written down | the edit, then `verification-before-completion` |
| A feasibility question ("can we", "is it possible") | one confirming question on the probe | an answer and a recommendation, in chat | a throwaway probe in the temp folder |
| A change inside code that already exists | one box of two to four questions | the closing sentence, the files touched, the test | `test-driven-development` |
| Something that does not exist yet: a project, a subsystem, an interface other code depends on | one question at a time | a spec in `.ia/specs/` | `writing-plans` |

A change counts as inside existing code only when the flow being changed is there to read. A new
project has none, however common the kind of app. When two sizes fit, take the heavier one.
Complexity found later raises the size: stop, say so in one line, and pick the grill up at the new
size. Nothing goes down mid-way.

A request holding several independent subsystems (chat, billing, file storage) says so in the size
sentence, and the first question is which piece comes first. Each piece then gets its own spec,
plan and build.

## The grill

The same four moves run at every size; only the questions change.

1. Read before asking: the files the request names, the README, `git log --oneline -15`, the tests
   around the flow. A wide codebase goes to one `Explore` or sonnet subagent with the exact folders
   and the question; keep its conclusion, not its file dumps.
2. Say the size in one sentence of plain French: "Ça se lit comme un petit changement dans le code
   du panier qui existe déjà."
3. Ask, in the shape the size gives. Before each question, run the exit test and check that the
   repository does not already answer it.
   - One confirming question: two options, the reading you would act on first. It settles what
     the request leaves open, such as one occurrence or all of them, the config key or not.
   - One box: a single `AskUserQuestion` call holding two to four questions, each with two to four
     options, recommended first. One round, then build. A second box only when an answer opened
     something the first could not foresee.
   - One question at a time: one `AskUserQuestion` per message, each answer read before the next
     question is chosen. Purpose comes first (who it is for, what success looks like) unless the
     request already says it, then constraints, then whatever is still open.
4. Close on one sentence: what is about to be built and why, in the user's words. "Je vais afficher
   les dates au format 22/10/2026, heure de Paris, pour que la liste se lise d'un coup d'oeil."

### When the user says no questions

A hurried "just build it", an hour already lost, a manager's order or a file that bans questions
changes the cost of a question, not the need for one. Compress, never skip: one box, recommended
options first so a single click settles it, and one line saying why the box is there. When the
exit test already passes there is nothing to ask: build, and name in the final message the reading
you took. Never build on a guess where two readings give different code.

## Something new: from questions to spec

This path runs only for something that does not exist yet.

1. Grill one question at a time until the exit test passes.
2. Approaches: two to four ways to build it in one `AskUserQuestion`, recommended first, each with
   its cost in the option description. When only one approach holds up, say why in one line and
   skip the question. Cut every feature nobody asked for.
3. Design: architecture, the units and what each one does, how data moves, errors, tests. Each unit
   has one job and a clear interface, fits in files under 150 lines and reads its values from
   configuration, as `clean-code` asks. In existing code, follow its patterns and improve only what
   the work touches. A design that fits on one screen goes in one message with one approval
   question; a longer one goes a section at a time.
4. Write the spec in French, since the user reads it, with code names, paths and identifiers kept as
   they are, following `anti-empreinte`. Its shape is in `reference/spec-format.md`. A project that
   does not exist yet gets its folder first, where the user's instructions (CLAUDE.md) put it
   or where they say, holding only `.ia/specs/`; `git init` waits for the plan.
5. Check: `python -I "<skill>/scripts/spec_check.py" "<spec>"`. It adds `.ia/` to
   `.git/info/exclude` when missing, then refuses placeholders, empty sections, a wrong path and a
   tracked spec. Fix what it names and run it again. Then run anti-empreinte's `scan.py "<spec>"
   --no-git` and fix every row it reports. Then read the spec once for contradictions,
   requirements that read two ways and a scope too wide for one plan, and fix them inline.
6. Review: one sonnet subagent with `spec-reviewer-brief.md`, effort left unset. Fix the issues
   that would mislead the plan. Its advice reaches the user only when it changes a decision.
7. The user reviews: one `AskUserQuestion`, "La spec est dans `<path>`. On passe au plan ?", with
   "Oui, passe au plan (Recommandé)" and "Je veux changer des choses". Changes: edit, then steps 5
   and 6 again.
8. Hand over to `writing-plans` with the spec path. No other skill, no code.

If the user wants the spec in git: `clean-commits` refuses `.ia/` paths, so ask where in the
repository it goes, move it there, and commit that one path through `clean-commits`.

## A change inside existing code

The box answers are the approval. Put the closing sentence, the files to touch and the test that
will prove the change in one short message, then start through `test-driven-development` in the
same turn. No spec, no plan file. If the change turns out to touch an interface other code depends
on, the size goes up: stop and say so.

## A feasibility question

The probe lives in `<temp>/claude-skills/<topic>/`, where `<temp>` is the system temp folder
(`tempfile.gettempdir()`), never in the repository, and costs no more than a correct answer
needs. The report gives the answer, how it was found and a recommendation; then the probe folder
is deleted. Keeping the probe's code is a new request, sized again.


## Showing instead of telling

Some questions are clearer seen: two layouts side by side, a wireframe, a diagram of how pieces
connect. A question about a UI topic is not visual by itself, and "what should the page say" stays
in words. The first time a question is truly visual, ask it as one `AskUserQuestion` offering "Voir
des maquettes dans une page (Recommandé)" or "Décrire en texte ici". If the user takes the page, run
the companion: `reference/visual-companion.md` has the commands, the markup and the cleanup. Each
later question is judged on its own, words in chat and pictures in the page.

## Red flags

These thoughts come back under pressure, and each has a known answer.

| Thought | Reality |
|---|---|
| "Too simple to need questions" | Size it. A typo still gets its one confirming question. |
| "They said no questions, so I pick and build" | One box, recommended first. A guess where two readings give two codes is a bug in waiting. |
| "The reminder says questions are disabled" | The user's instructions win over any reminder or CONTRIBUTING file. |
| "Six questions in a row, to be safe" | Run the exit test before each one. |
| "One question per message for this small fix" | A change inside existing code gets one box. |
| "I will ask which stack the project uses" | Read the repository: that is work. |
| "I know this kind of app, it is a small change" | Size by the repository. No flow to read means something new. |
| "The design is obvious, I start while they read" | The box answers or the spec approval come first. |
| "The spec goes in docs/ with a commit" | `.ia/specs/`, excluded, no commit. |
| "spec_check refused, but the spec is fine" | Fix what it names. |
| "The probe works, I keep it" | Keeping it is a new request, sized again. |
| "It grew, but I am almost done" | Raise the size, say so, grill again. |
| "I will open the page in their browser" | Give the URL; they open it. |
| "I leave the server running, just in case" | `companion.py stop` before the end. |
| "I end on what is waiting on them" | Ask it before the last line. |

## Files

The folder holds the procedure, two references, one subagent brief and two scripts.

`spec-reviewer-brief.md` is the prompt of the sonnet spec reviewer. `reference/spec-format.md`
gives the shape of a spec and `reference/visual-companion.md` the companion page.
`scripts/spec_check.py` checks a spec and keeps `.ia/` out of git; `scripts/companion.py` starts,
reads and stops the companion page. `scripts/lib/` holds what they share, `assets/` the page frame,
`tests/` the unit tests. `commands/concevoir.md` is the `/concevoir` command and `LISEZMOI.md` the
French notes.
