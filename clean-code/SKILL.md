---
name: clean-code
description: Use when the user types /clean-code, asks to audit or tidy a project's code, or a file or folder has grown too long or crowded. Also holds the writing rules for code this skill writes itself.
---

# Clean code

An audit measures a scope against rules 0 to 19, keeps the findings a fresh agent confirmed, and
turns them into a note out of 20. Below 20 it writes a plan, asks how much to apply, and applies it
step by step, one commit per step.

`<skill>` is this skill's base directory. Call scripts by absolute path with `python -I`, from the
project root: `python -I "<skill>/scripts/measure.py" src`. They never crash: on failure they print
what to do by hand.

Everything the audit writes goes to `.ia/clean-code/<run>/` at the project root (`measure.json`,
`findings.json`, `score.json`, `plan.md`), plus an optional `config.json` next to the runs holding
the thresholds. The scripts add `.ia/` to `.git/info/exclude`. Outside git, or when the project must
stay untouched, `measure.py --out <folder>` puts the run elsewhere and the other scripts take
`--run <run folder>`. Scratch files go to `<temp>/claude-skills/clean-code-<run>`, deleted at the
end. Delete nothing you did not create.

## Rules that never bend

These hold in every mode, whatever the user asks.

1. Read-only until `plan_check.py` prints `plan ok`: nothing written in the project apart from
   `.ia/`.
2. Scope first: the `/clean-code` argument, else one question. In doubt, the narrowest. Outside the
   scope, findings are reported, never fixed.
3. A finding needs `file:line` and a proof. Verdicts come from a fresh agent that never saw the
   measuring, never from you.
4. The repository is shared with other sessions: commit only your own paths, never `git add .`,
   never on a red check, never push, no stash, revert or clean on changes you did not make.
5. Removed code is deleted, git keeps it. Outside git, move it to `old/`.
6. Visual checks go through the `chrome-bidi` skill, headless.
7. No attribution to any AI tool anywhere. Pushed history is never rewritten: the user decides.

## The rules

Defaults of the thresholds in brackets. "Script" means a module under `scripts/checks/`.

0. A bad practice outside the grid, weighed 0.5 to 3 points. A secret in a tracked file is rule 0
   with the `secret` cap, lifted only by the verifier for a placeholder or sample value.
1. At most `max_lines` [150] lines per file, tests included, test data excepted. Script.
2. One file, one job.
3. No dead code: unimported files, unused imports and symbols, commented-out code, unreferenced
   images. Script, confirmed by reading.
4. At most `max_files` [8] code files per folder, unless the framework imposes the layout. Script.
5. Look-alike code is merged, both locations proven.
6. `max_function_lines` [40], `max_params` [4], `max_nesting` [3], one job per function. Script.
7. Names say what they hold, one word per concept: `reference/naming.md`.
8. Errors handled, state immutable by default, strict types: no `any`, no silenced check, no
   swallowed error (`swallowed` cap when it hides a failure on a path that matters). Script.
9. Everything testable through the public API is tested. Script for "no test at all".
10. Dev and test code never ships: debug output, seeds, fixtures, test accounts (`test-in-prod` cap
    when it reaches the production build). Script.
11. Nothing built into production that it does not need.
12. Lint, format, typecheck, build and tests are configured and pass. The `build` cap is for a
    failing typecheck or build; a failing suite is a finding without cap. Script for the config.
13. No LLM fingerprint: `reference/fingerprint.md` (`attribution` cap for an attribution to any AI
    tool). Script.
14. No comment in code. Lines a tool reads stay: linter and compiler directives, shebang, imposed
    licence header, bundler magic comments, and doc comments of the public API (files exported by
    the manifest and paths listed in `public_api`). Script.
15. Every identifier in English: `reference/naming.md`. Script.
16. Every variable optimised: `reference/variables.md`.
17. Text shown to the user lives in the translation files, same keys in every language. Only when
    the project already has them. Script.
18. As few hardcoded values as possible: `reference/values.md`. Script.
19. Every image WebP, cropped to its box, at 1x and 2x; an SVG stays SVG: `reference/images.md`.
    Script, live boxes through `chrome-bidi`.

`score.py` starts from 20 and deducts only for confirmed findings:

| Rule | Deduction |
|---|---|
| 0 | the points of each finding |
| 1 | share of code files over the limit: 0.5 under 10 %, 3 over 40 %, linear between |
| 14, 15, 18 | 2 times the share of files carrying the defect |
| 12 | 1 per finding, 2 at most |
| 2, 5, 9, 10 | 0.5 per finding, 2 at most |
| 11 | 0.5 per finding, 1 at most |
| 3, 6, 8, 13, 16, 17, 19 | 0.25 per finding, 2 at most |
| 4, 7 | 0.25 per finding, 1 at most |

Caps hold the note down, the lowest wins: `secret` 5, `build` 8, `swallowed`, `test-in-prod` and
`attribution` 10. The note is rounded to the half point.

## Writing code

Rules 14 to 19 and the size limits bind every line this skill writes. Paste this into the prompt of
every subagent that writes code:

`````text
Code rules for this task:
- No comment in the code, except lines a tool reads (linter directives, shebang, licence header)
  and doc comments of the public API. What a comment would explain goes into a name.
- Every identifier in English. Text shown to the user keeps its language.
- No hardcoded value: compute it, read it from config, or name it once.
- Every variable optimised: cheapest correct type, right structure, nothing allocated in a hot
  loop, const by default, smallest scope.
- If the project has translation files, user-facing text goes there in every language at once, same
  keys. Existing gaps are reported, not filled.
- Images go in as WebP cropped to their box at 1x and 2x through <skill>/scripts/apply/fit_image.py.
- A file stays under 150 lines and a folder under 8 code files: split before crossing.
- Visual checks go through chrome-bidi, headless.
- Typecheck, lint and tests run through the project's package manager, never npx.
- Defects in code you did not touch are reported, not fixed.
- No `shortcut:` or other note comment either: name the shortcut in your reply.
`````

A comment your change makes false leaves with the code it described. Other existing comments wait
for a clean-code pass, so a diff never mixes a fix and a comment sweep.

## Audit

In this order, each step ending before the next.

1. Scope: the `/clean-code` argument, else `AskUserQuestion`: whole project, then each app or top
   folder, narrowest first.
2. Measure: `python -I "<skill>/scripts/measure.py" <scope>`. It prints the run folder, candidates
   by rule and, past `reader_threshold` [150] code files, the reader batches.
3. Images, when the scope has some and the project renders pages: measure live boxes, then measure
   again with `--boxes` before any verdict (`reference/images.md`).
4. Commands, one heavy process at a time, low priority, two workers at most: typecheck without
   cache, linter with `--max-warnings 0`, the build only when it writes outside the tree, the test
   suite. A failure is a rule 12 finding with its output. A command that cannot run is
   `findings.py unmeasured --rule 12 --why "<reason>"`, never installed.
5. Read. Up to `reader_threshold` files, read them yourself. Past that, map the scope first when
   `graphify` is on the PATH, with
   `GRAPHIFY_OUT="<absolute project root>/.ia/graphify-out" graphify update <scope>`: no model call,
   never its skill. The graph goes to `.ia/graphify-out/`, never into the scope, and `.ia/`, which git
   ignores since step 2, stays out of the scan and the measure. A relative `GRAPHIFY_OUT` would land
   under `<scope>`. Then one agent
   per batch, `readers` at most [4], prompt from `reader-brief.md`, all in one message. Every reading rule ends with findings, `findings.py checked --rule <n> --why "..."` or
   `findings.py unmeasured --rule <n> --why "..."`.
6. Verify: one fresh Agent call (never a fork), prompt from
   `verify-brief.md` with its `<...>` filled. Disagree with a verdict only by sending it back with
   the proof it missed.
7. Score: `python -I "<skill>/scripts/score.py"`. It refuses while a candidate has no verdict or a
   reading rule is uncovered. At 20, stop: no plan, no question.
8. Plan: write `<run>/plan.md` from `plan-template.md`, in English, then run
   `python -I "<skill>/scripts/plan_check.py"` until it prints `plan ok`.
9. Print the note alone as a heading, `# 12/20`, with no word around it, then apply the whole
   plan without asking.

## Apply

Steps run in phase order; splitting files comes last, once the tests guard it.

| Phase | Rules |
|---|---|
| 1 | 12 |
| 2 | 9 |
| 3 | 0, 3, 7, 8, 13 to 19 |
| 4 | 5, 6 |
| 5 | 1, 2, 4 (`git mv`) |
| 6 | 10, 11, secrets |

For each step of the plan:

1. Check its files have not moved since the plan (`git status`, `git diff`). One that moved belongs
   to another session: skip it and say so.
2. Change the listed files only, then run the step's check and the tests of the touched files.
3. Green: commit through the `clean-commits` skill as a caller, with the step's `Files:` paths
   only (deleted ones included), no push. Without that skill, stop and say so.
4. Red: restore the step's own files, report the output, continue only with steps that do not
   depend on it.

At the end of each phase, run the typecheck without cache and the full suite. Red: revert the
phase's step commits newest first with `git revert --no-edit` until it turns green. The last one
reverted broke it: report its output. Bring back the newer ones by reverting their revert commits
and run the suite again; one that turns it red goes back out and is reported with the culprit.

A secret moves to the environment with a sample entry in `.env.example`. If it was ever committed it
has leaked: ask whether to rotate it, and never print it. A UI step ends with before and after
screenshots at phone and desktop widths.

After the last step, measure, verify and score again on the same scope.

## Report

The note after alone as a heading, `# 17/20`, then in the user's language each step with its commit
hash, the raw output of the last full suite, and what is left with its reason. A question comes
only for what the user alone decides, such as rotating a leaked secret.

## Files

A new module in `scripts/checks/` with a `check(files, root, config)` function joins the measure.
Tests: `python -I -B -m unittest discover -s tests -p "test_*.py"` from this folder.
