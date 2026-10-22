---
name: clean-code
description: Use when auditing, tidying or refactoring a project's code, when the user types /clean-code, when a file has grown long or a folder crowded, and every time code is written or edited in any task, since its writing rules (no comments, English names, optimised variables, no hardcoded values, images fitted to their box, visual checks through headless chrome-bidi) hold outside audits too.
---

# Clean code

## Overview

Once per session, before following this skill, run
`python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"` and read the line it prints.
When that file does not exist, go on without it. After a line that starts with `updated`, read this file again
before going on.

An audit measures a scope against twenty rules, numbered 0 to 19, and turns the findings a fresh
agent confirmed into a note out of 20. Below 20 it writes a plan, asks how much of it to apply,
and applies it step by step, one commit per step. Rules 14 to 19 and the size limits also bind
every line of code written in any other task: see "Writing code".

File names below sit in this skill's base directory (shown when the skill loads, otherwise
`$CLAUDE_CONFIG_DIR/skills/clean-code`, or `~/.claude/skills/clean-code` when the variable is
empty). Call the scripts by absolute path with `python -I`, the path in forward slashes inside
double quotes, from the project root: `python -I "<skill>/scripts/measure.py" src`. They
never crash: on failure they print what to do by hand.

Everything the audit writes goes to `.ia/clean-code/` at the project root: one folder per run
holding `measure.json`, `findings.json`, `score.json` and `plan.md`, plus an optional
`config.json` next to the runs. The scripts add `.ia/` to `.git/info/exclude`, so none of it is
ever committed. Outside a git repository, or when nothing may be written in the project,
`measure.py --out <folder>` puts the run there, and the other scripts take `--run <run folder>`.
Scratch files go to a folder this run creates,
`<temp>/claude-skills/clean-code-<run>`, where `<temp>` is the system temp folder
(`tempfile.gettempdir()`), deleted at the end. Never delete a
folder or a file you did not create: another session may own it.

## Rules that never bend

These hold in every phase, whatever the dose.

1. The audit is read-only until the user answers the dose question. No edit, rename, move,
   commit, dependency install, or command that writes into the project, apart from `.ia/` and
   the one `.ia/` line the scripts add to `.git/info/exclude`. Silence, "ok" or "continue" is no
   answer: ask again. Do not start "the obvious part" while waiting, even when the prompt asks
   for it.
2. The scope comes first: the `/clean-code` argument, else one question. In doubt, the narrowest
   scope, said out loud. Outside the scope, findings are reported, never fixed.
3. Only confirmed findings count, and a finding without `file:line` and a proof is a guess. The
   verdicts come from a fresh agent that never saw the measuring, never from you.
4. The repository is shared with other sessions. Commit only your own paths, never `git add .`,
   never on a red suite, never push. Uncommitted changes you did not make are someone's work:
   no stash, no revert, no clean.
5. Removed code is deleted: git keeps it. A folder outside git gets `old/` instead.
6. Every visual check goes through the `chrome-bidi` skill, headless: no window ever opens on the
   user's screen.
7. Never an attribution to Claude or any other AI tool, in a commit, a file or a plan, and nothing
   written that the `anti-empreinte` skill forbids. History already pushed is never rewritten by
   this skill: the user decides.
8. Done means checked: a step is green when you have read the suite output, not when it ran.

## The rules

Each rule names what measures it: a script under `scripts/checks/`, reading, or both. The
thresholds come from `config.json`, defaults in brackets.

0. A bad practice outside the grid, confirmed, weighed 0.5 to 3 points on its own. A secret in a
   tracked file is rule 0 with the `secret` cap. Only the verifier lifts it, for a placeholder or
   a sample value; a key you guess is a demo one keeps the cap. Script and reading.
1. A file holds at most `max_lines` lines [150], tests included, test data excepted. Script.
2. One file, one job. Reading.
3. No dead code: files nothing imports, unused imports and symbols, commented-out code, images no
   file references. Script, confirmed by reading.
4. A folder holds at most `max_files` code files [8], unless the framework imposes the layout.
   Script.
5. Code that looks alike is merged, both locations proven. Reading.
6. Short functions: `max_function_lines` [40], `max_params` [4], `max_nesting` [3], one job.
   Script and reading.
7. Names say what they hold, one word per concept: `reference/naming.md`. Reading.
8. Errors are handled, state is immutable by default, types are strict: no `any`, no silenced
   check, no swallowed error (the `swallowed` cap when it hides a failure on a path that
   matters). Script and reading.
9. Everything testable through the public API is tested. Script for "no test at all", reading for
   the rest.
10. Dev and test code never ships: debug output, seeds, fixtures, test accounts (the
    `test-in-prod` cap when it reaches the production build). Script and reading.
11. What production does not need is not built into it. Reading.
12. Lint and formatter are configured and pass, and so do the typecheck, the build and the test
    suite. The `build` cap is for a typecheck or a build that fails; a suite that fails or cannot
    start is a finding without cap. Script for the config, commands for the rest.
13. No LLM fingerprint: `reference/fingerprint.md`, with the `anti-empreinte` skill as the full grid
    (the `attribution` cap for an attribution to any AI tool). Script and reading.
14. No comment in code. Lines a tool reads stay: linter and compiler directives, the shebang, an
    imposed licence header, bundler magic comments. Doc comments of the public API stay too: the
    files the manifest exports (`exports`, `main`, `module`, `types`) and the paths listed in
    `public_api`. Script.
15. Every identifier is in English: `reference/naming.md`. Script and reading.
16. Every variable is optimised: `reference/variables.md`. Reading.
17. Text shown to the user lives in the translation files, with the same keys in every language.
    Only when the project already has translation files. Script.
18. As few hardcoded values as possible: computed, read from config, or named once:
    `reference/values.md`. Script and reading.
19. Every image is WebP, cropped to its box, at 1x and 2x; an SVG stays SVG:
    `reference/images.md`. Script, live boxes through `chrome-bidi`.

`score.py` starts from 20 and takes off, per rule, only for confirmed findings:

| Rule | Deduction |
|---|---|
| 0 | the points of each finding |
| 1 | share of code files over the limit: 0.5 under 10 %, 3 over 40 %, linear between |
| 14, 15, 18 | 2 points times the share of files carrying the defect |
| 12 | 1 per finding, 2 at most |
| 2, 5, 9, 10 | 0.5 per finding, 2 at most |
| 11 | 0.5 per finding, 1 at most |
| 3, 6, 8, 13, 16, 17, 19 | 0.25 per finding, 2 at most |
| 4, 7 | 0.25 per finding, 1 at most |

A cap holds the note down whatever the rest: `secret` 5, `build` 8, `swallowed`, `test-in-prod`
and `attribution` 10. The lowest cap wins. The note is rounded to the half point.

## Writing code, in any task

These hold for every line written or edited, tests included, audit or not. Paste them into the
prompt of every subagent that writes code, word for word apart from `<skill>`, which becomes the
base directory:

`````text
Code rules for this task:
- No comment in the code. Only lines a tool reads stay (linter directives, shebang, licence
  header) and doc comments of the public API. What a comment would explain goes into a name.
- Every identifier in English: variables, functions, classes, files, keys. Text shown to the
  user keeps its language.
- No hardcoded value: compute it from what it depends on, read it from config, or name it once.
- Every variable optimised: cheapest correct type, right structure, nothing allocated in a hot
  loop, const by default, smallest scope.
- If the project has translation files, text shown to the user goes there, in every language at
  once, same keys. Gaps already there are reported, not filled.
- An image goes in as WebP cropped to its box at 1x and 2x, through
  <skill>/scripts/apply/fit_image.py; an SVG stays SVG.
- A file stays under 150 lines and a folder under 8 code files: split before crossing.
- Any visual check goes through the chrome-bidi skill, headless, never in a visible window.
- Typecheck, lint and tests run through the project's package manager (pnpm exec, npm run),
  never npx, which can fetch a stand-in and report nothing.
- These rules bind the lines you write. Defects in code you did not touch are reported in your
  answer, not fixed.
`````

A comment your change makes false leaves with the code it described. The other existing ones wait
for a clean-code pass: a diff mixing a fix and a comment sweep cannot be reviewed.

## Audit

The audit runs in this order, and each step ends before the next one starts.

1. Scope. Take the `/clean-code` argument. Without one, ask with `AskUserQuestion`: the whole
   project, then each app or top folder the repo actually has, narrowest first.
2. Measure: `python -I "<skill>/scripts/measure.py" <scope>`. It prints the run folder, the
   candidates by rule and, past `reader_threshold` code files [150], the reader batches.
   Thresholds live in `.ia/clean-code/config.json`; create it only when the user wants other
   limits.
3. Images, when the scope has some and the project renders pages: measure the live boxes and
   measure again with `--boxes`, before any verdict (`reference/images.md`, step 2).
4. Commands, one heavy process at a time, at low priority, two workers at most: the typecheck
   without cache (`tsc --noEmit --incremental false`), the linter with `--max-warnings 0`, the
   build when it writes outside the tree only, the test suite. Through the project's package
   manager (`pnpm exec`), never `npx`, which can install a stand-in and report no errors. A failure
   becomes a rule 12 finding with its output, `--cap build` for the typecheck and the build only.
   A command that cannot run (no `node_modules`, no compiler) is `findings.py unmeasured --rule 12`
   with the reason, never installed. It only names what could not run: the rule 12 findings the
   measure made still count.
5. Read. Up to `reader_threshold` code files, read them yourself. Past that, one reader agent per
   batch, `readers` at most [4], sonnet at medium effort, prompt from `reader-brief.md`, all in
   one message. Every rule measured by reading ends with findings, or `findings.py checked --rule
   <n> --why "<what was read>"`, or `findings.py unmeasured --rule <n> --why "<reason>"`.
6. Verify. One fresh agent, sonnet at medium effort: a new Agent call, never a fork, whose prompt
   is the filled `verify-brief.md` block, each `<...>` replaced (`<skill>` by this folder's
   path). It refutes what it can and sets every verdict. Disagree with a verdict only by sending
   it back with the proof it missed.
7. Score: `python -I "<skill>/scripts/score.py"`. It refuses while a candidate has no verdict or
   a reading rule is uncovered. It prints the note, the deductions, the cap, the comparison with
   the previous run and one line per confirmed finding. At 20, stop: no plan, no question.
8. Plan: copy the shape of `plan-template.md` into `<run>/plan.md`, in French, every confirmed id
   in one step or left as is with its reason. `python -I "<skill>/scripts/plan_check.py"` until
   it prints `plan ok`.
9. Ask with `AskUserQuestion`, the plan path in the question: "Tout le plan", "Les etapes sures
   seulement", "Rien, garder la note et le plan". Nothing is touched before the answer.

## Apply

Steps run in phase order, safest first; splitting files comes last, once the tests guard it.

| Phase | Rules | Why here |
|---|---|---|
| 1 | 12 | lint and format first, so later diffs stay readable |
| 2 | 9 | the safety net before any refactor |
| 3 | 0, 3, 7, 8, 13 to 19 | local fixes, one file at a time |
| 4 | 5, 6 | functions and duplication |
| 5 | 1, 2, 4 | splitting files and folders, with `git mv` |
| 6 | 10, 11, secrets | what can break production without a red test |

For each step of the chosen dose:

1. Check that its files have not moved since the plan (`git status`, `git diff` on those paths).
   One that moved belongs to another session now: skip it, say so, go on.
2. Make the change on the listed files only, then run the step's check, the typecheck without
   cache and the full suite. Read the outputs.
3. Green: load the `clean-commits` skill and commit through it, as a caller: the step's
   `Fichiers :` paths only, deleted ones included, no push. Without that skill, stop and say so.
4. Red: restore the step's own files to their state before the step, report it with the output,
   and go on only with the steps that do not depend on it.

A secret leaves the code for the environment, with a sample entry in `.env.example`. If it was
ever committed it has leaked: ask with `AskUserQuestion` whether to rotate it, and never print it.
A UI step ends with headless screenshots through `chrome-bidi`, before and after, phone and
desktop widths, compared.

After the last step, measure, verify and score again on the same scope: `score.py` prints the
progress against the run before.

## Report

In French, in the terminal: the note before and after, each step with its commit hash, the raw
output of the suites, and what is left with its reason (outside the scope, refuted, left as is,
refused by the user, skipped because another session moved the file). Nothing else is written.

## Red flags

Each of these thoughts has let a rule slip before.

| Thought | What to do |
|---|---|
| "This fix is obvious, I'll do it while the user reads" | Nothing moves before the answer. |
| "I measured it, I can confirm it" | A fresh verifier confirms. |
| "The script found nothing, rule 5 is fine" | Rule 5 is read, then declared checked. |
| "A doc comment explains the API, I'll keep this one" | Only the public API keeps them. |
| "The magic number is obvious here" | Compute it, configure it, or name it. |
| "A quick look in a browser window" | `chrome-bidi`, headless. |
| "The image looks fine, it's only 300 KB" | Fit it to its box, 1x and 2x WebP. |
| "The suite takes long, the typecheck passed" | Run the suite, read it, then commit. |
| "I'll stage everything, it's all cleanup" | Commit the step's own files only. |
| "The old file goes to old/ to be safe" | Inside git, delete: history keeps it. |
| "The attribution is pushed, a quick force-push fixes it" | Ask the user. |
| "The purple gradient is a design choice" | Only if the user chose it: plan a step, the dose decides. |
| "This key looks like a demo one" | The verifier decides; the cap holds until it refutes. |
| "The key is in .env.example now, done" | Ask about rotating the leaked key. |

## Files

`scripts/measure.py` measures; `scripts/findings.py` lists, adds and judges findings, safe with
four writers at once; `scripts/score.py` computes the note; `scripts/plan_check.py` checks the
plan; `scripts/apply/fit_image.py` fits an image. `scripts/checks/` holds one module per family of
checks, loaded on its own: a new file there with a `check(files, root, config)` function joins the
measure. `scripts/lib/` holds what they share: the lexer, the file walk, the run folders and the
config, the findings store and its lock, the image headers. `reference/` holds the long rules,
`plan-template.md` the plan, `reader-brief.md` and `verify-brief.md` the agent prompts,
`commands/clean-code.md` the command, `tests/test_pure.py` the unit tests of the pure parts
(`python -I -B -m unittest discover -s tests -p "test_*.py"`).
