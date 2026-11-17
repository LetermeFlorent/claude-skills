---
name: clean-code
description: Use when the user types /clean-code, asks to audit or tidy a project's code, or a file or folder has grown too long or crowded.
---

# Clean code

Audit measures scope against rules 0 to 19, keeps findings a fresh agent confirmed, turns them into
note out of 100, no floor: many findings take it below 0. Below 100: write plan, `plan_check.py` approves it, apply whole plan without asking,
one commit per step.

`<skill>` = this skill's base directory. Scripts by absolute path with `python -I`, from project
root: `python -I "<skill>/scripts/measure.py" src`. Never crash: on failure they print what to do by
hand.

Audit writes only to `.ia/clean-code/<run>/` at project root (`measure.json`, `findings.json`,
`score.json`, `plan.md`), plus optional `config.json` next to runs holding thresholds. Scripts add
`.ia/` to git's `info/exclude`. Outside git, project root = scope folder. Other scripts take
`--run <run folder>`. Scratch files: `<temp>/claude-skills/clean-code-<run>`, deleted at end. Delete
nothing you did not create.

## Rules that never bend

Hold in every mode, whatever user asks.

1. Read-only until `plan_check.py` prints `plan ok`: nothing written in project apart from `.ia/`.
2. Scope and passes first: `/clean-code` argument, else one question. In doubt, narrowest. Outside
   scope, findings reported, never fixed.
3. Finding needs `file:line` and proof. Verdicts come from fresh agent that never saw measuring,
   never from you.
4. Repository shared with other sessions: commit only your own paths, never `git add .`, never on
   red check, never push, no stash, revert or clean on changes you did not make.
5. Removed code deleted, git keeps it. Outside git, move it to `old/`.
6. Visual checks through `browser-bidi` skill, headless.
7. No attribution to any AI tool anywhere. Pushed history never rewritten: user decides.

## The rules

Threshold defaults in brackets. "Script" = module under `scripts/checks/`.

0. Bad practice outside grid, weighed 2.5 to 15 points. Secret in tracked file = rule 0 with `secret`
   cap, lifted only by verifier for placeholder or sample value.
1. At most `max_lines` [150] lines per file, tests included, test data excepted. Script.
2. One file, one job.
3. No dead code: unimported files, unused imports and symbols, commented-out code, unreferenced
   images. Script, confirmed by reading.
4. At most `max_files` [8] code files per folder, unless framework imposes layout. Script.
5. Look-alike code merged, both locations proven.
6. `max_function_lines` [40], `max_params` [4], `max_nesting` [3], one job per function. Script.
7. Names say what they hold, one word per concept: `reference/naming.md`.
8. Errors handled, state immutable by default, strict types: no `any`, no silenced check, no
   swallowed error (`swallowed` cap when it hides failure on path that matters). Script.
9. Everything testable through public API is tested. Script for "no test at all".
10. Dev and test code never ships: debug output, seeds, fixtures, test accounts (`test-in-prod` cap
    when it reaches production build). Script.
11. Nothing built into production it does not need.
12. Lint, format, typecheck, build and tests configured and pass. `build` cap for failing typecheck
    or build; failing suite = finding without cap. Script for config.
13. No LLM fingerprint: `reference/fingerprint.md` (`attribution` cap for attribution to any AI
    tool). Script.
14. No comment in code. Lines a tool reads stay: linter and compiler directives, shebang, imposed
    licence header, bundler magic comments, doc comments of public API (files exported by manifest
    and paths listed in `public_api`). Script.
15. Every identifier in English: `reference/naming.md`. Script.
16. Every variable optimised: `reference/variables.md`.
17. Text shown to user lives in translation files, same keys in every language. Only when project
    already has them. Script.
18. As few hardcoded values as possible: `reference/values.md`. Script.
19. Every image WebP, cropped to its box, at 1x and 2x; SVG stays SVG: `reference/images.md`.
    Script, live boxes through `browser-bidi`.

`score.py` starts from 100, deducts only for confirmed findings, no limit per rule and no floor:

| Rule | Deduction |
|---|---|
| 0 | the points of each finding, 2.5 to 15 |
| 1 | share of code files over the limit: 2.5 up to 10 %, then 12.5 more per 30 % (15 at 40 %, 40 at 100 %) |
| 14, 15, 18 | 10 times the share of files carrying the defect |
| 12 | 5 per finding |
| 2, 5, 9, 10, 11 | 2.5 per finding |
| 3, 4, 6, 7, 8, 13, 16, 17, 19 | 1 per finding |

Caps hold note down, lowest wins: `secret` 25, `build` 40, `swallowed`, `test-in-prod` and
`attribution` 50. Note rounded down to whole point, so any deduction keeps it under 100.

## Writing code

Rules 14 to 19, size limits and the eight quality bullets below bind every line this skill writes. Paste this into prompt of every
subagent that writes code, `<skill>` replaced by absolute base directory, 150 and 8 by run's
`max_lines` and `max_files`:

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
- Visual checks go through browser-bidi, headless.
- Typecheck, lint and tests run through the project's package manager, never npx.
- Defects in code you did not touch are reported, not fixed.
- No `shortcut:` or other note comment either: name the shortcut in your reply.
- Secure by default: input hostile (validate, escape, parameterise queries, no shell or eval on user
  data), least privilege, no secret in code or logs, vetted crypto and libraries only, block every
  attack path seen. Code that must pass security scanners, or a security finding to fix: secure-code-loop
  skill runs scan, fix, rescan.
- Dependencies and tools always at latest stable release, version read from the registry, not memory;
  read changelog before bumping, tests green after.
- Never code from memory: read code, docs and installed version of what you use first, then write.
- Search before writing: grep project for existing function, helper, constant or dependency, reuse it;
  new code only when nothing found.
- Best readability: small functions, one job each, early returns, no clever trick.
- Solid code: every exception handled at each boundary (input, I/O, network, parsing, null, empty,
  out of range, concurrency); typed specific error, never swallowed.
- Best practices of language and framework; never work around rule, type, linter or test, fix cause.
- Easy to maintain: low coupling, explicit dependencies, no hidden state, one change touches one place.
`````

Comment your change makes false leaves with code it described. Other existing comments wait for
clean-code pass: diff never mixes fix and comment sweep.

## Audit

In this order, each step ending before next.

1. Scope and passes: from `/clean-code` argument, else one `AskUserQuestion` holding both questions.
   Scope: narrowest app or top folder first (recommended), wider ones next, whole project last.
   Passes: `Until over 90/100` (recommended), `1 pass`, `2 passes`, `3 passes`; any other count or
   target note the user types is taken as given. Caller that forbids questions and names none: 1 pass.
2. Measure: `python -I "<skill>/scripts/measure.py" <scope>`, scope of several folders or files as
   several arguments. Prints run folder, candidates by rule and, past `reader_threshold` [30] code
   files, reader batches. Imports and image references count from whole project, findings only in
   scope.
3. Images and AI traces. When scope has images and project renders pages: measure live boxes, then
   measure again with `--boxes` before any verdict (`reference/images.md`). Then, images or not, run
   `python -I "<skill>/../strip-ai-traces/scripts/scan.py" <path> --no-git` on each path of scope.
   Add only hits markers.py cannot see (vocabulary, Title Case headings, bold lead-ins, README
   outline, metadata), on files with no row in `findings.py list --rule 13`, each with
   `findings.py add --rule 13 --source scan`.
4. Commands, one heavy process at a time, low priority, two workers at most: typecheck without
   cache, linter with `--max-warnings 0`, build only when its output can go to scratch folder, test
   suite. Failure = rule 12 finding with its output. Command that cannot run never installed; it
   goes, with build that would write into project, into one
   `findings.py unmeasured --rule 12 --why "<each command and its reason>"`: second call replaces
   first.
5. Read. Up to `reader_threshold` files, read them yourself. Past that, one agent per batch,
   `readers` at most [4], prompt from `reader-brief.md`, all in one message. Before reading,
   map scope with `python -I "<skill>/../code-map/scripts/code_map.py" build --root "<absolute project
   root>" --scope <scope>`: no model call. Map goes to `.ia/code-map/`; `.ia/`, git-ignored since
   step 2, stays out of scan and measure. Every
   reading rule (2, 5, 7, 9, 11, 16) ends with findings,
   `findings.py checked --rule <n> --why "..."` or `findings.py unmeasured --rule <n> --why "..."`.
6. Verify, only when `python -I "<skill>/scripts/findings.py" list --status candidate` prints
   `| candidate |` row: one fresh Agent call (never fork), prompt from `verify-brief.md` with its
   `<...>` filled. Disagree with verdict only by sending it back with proof it missed.
7. Score: `python -I "<skill>/scripts/score.py"`. Refuses while candidate has no verdict or reading
   rule uncovered. At 100, stop: no plan, no question.
8. Plan: write `<run>/plan.md` from `plan-template.md`, in English, then run
   `python -I "<skill>/scripts/plan_check.py"` until it prints `plan ok`.
9. Print note alone as heading, `# 62/100` (or `# -40/100`), no word around it, then apply whole plan without asking.

## Apply

Steps run in phase order; files split only after tests and merges are in.

| Phase | Rules |
|---|---|
| 1 | 12 |
| 2 | 9 |
| 3 | 0, 3, 7, 8, 13 to 19 |
| 4 | 5, 6 |
| 5 | 1, 2, 4 (`git mv`) |
| 6 | 10, 11, secrets |

What failed in audit step 4, listed on plan's `Suite:` line, is baseline. Check in this section,
step's own check included, red only when something fails not on that list; test or error a step
fixes comes off it.

For each step of plan:

1. Check its files have not moved since plan (`git status`, `git diff`). One that moved belongs to
   another session: skip it, say so.
2. Change listed files only, then run step's check and tests of touched files.
3. Green: commit through `clean-commits` skill as caller, step's `Files:` paths only (deleted ones
   included), no push. Without that skill, stop, say so. Refusal (`FAILED`, red hook) counts as red.
4. Red: restore step's own files, report output or refusal text, continue only with steps that do
   not depend on it.

End of each phase that applied at least one step: typecheck without cache and full suite. Red:
revert phase's step commits newest first with `git revert --no-edit` until green. Last one reverted
broke it: report its output. Bring back newer ones by reverting their revert commits, run suite
again; one that turns it red goes back out, reported with culprit.

Secret moves to environment with sample entry in `.env.example`. Ever committed = leaked: ask whether
to rotate it, never print it. When caller forbids questions, never rotate secret or rewrite history;
list them under `Left as is`, hand back to caller. UI step ends with before and after screenshots at
phone and desktop widths.

After last step, run audit steps 2 to 7 again on same scope, reading limited to files plan changed.
That ends one pass. Next pass (audit steps 8 and 9 on this new score, then Apply) while count chosen
is not reached, or note not over target chosen. Stop also at 100, or when a pass leaves note no
higher than pass before; say why it stopped.

## Report

Note after alone as heading, `# 85/100`, then in user's language note after each pass, each step
with its commit hash, raw output of last full suite, what is left with its reason. Question only for
what user alone decides, such as rotating leaked secret.

## Files

New module in `scripts/checks/files/` (per file) or `scripts/checks/project/` (whole scope) whose
`check(files, root, config)` returns `(findings, stats)` joins measure; `config["project_files"]`
holds every project file.
Tests: `python -I -B -m unittest discover -s tests -p "test_*.py"` from this folder.
