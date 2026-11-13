---
name: writing-skills
description: Use when a skill must be created, edited or reviewed, when the user types /write-skill, when a fail-then-success lesson should be kept as a skill, or when an existing skill does not trigger or gets skipped under pressure.
---

# Writing skills

Skill worth writing only for what an agent does wrong without it, so baseline first: fresh subagent runs a
real task with no skill; its exact choices and excuses are the material. Already does the right thing: no
skill. Fails: write the smallest text answering that failure, rerun same task with the skill, close the
loopholes runs still show. Constraint a regex or hook can enforce = script or hook, not skill; account of
one session is not a skill.

Examples in `<claude-skills>`, parent folder of this skill's own folder (its base directory, link
resolved): open the closest before writing.

## Rules

These hold for new skill, edit and remaster; a lesson keeps only what the Lessons section names.

1. Baseline decides whether a skill exists. New skill: against no skill. Edit: against current version,
   only when the edit changes what an agent does. Fail-then-success lesson from this session is its own
   baseline: write down command, output and wrong belief word for word, then write the skill. Wrong path,
   name or command needs no baseline: run the thing it names. Draft written before the baseline is no
   evidence. Draft this run did not create is never deleted: ask.
2. Description starts with "Use when", lists triggers only: situations, symptoms, error text, the command
   (`/name`). Never steps: agent finding the procedure there follows the summary, skips the body. Skill
   triggering too rarely gets more trigger words.
3. "Tested" = a run happened in this session and you read its report. Optional `## What was tested`
   section of `README.md` written after the runs from what they did, failures and gaps included, never
   ahead. User asks to skip tests: one sentence on what an untested skill costs, then AskUserQuestion with
   "Test before delivering (Recommended)" first; test until they answer. They pick no tests: section is
   `## Not tested yet`.
4. Skill name and command the user will type get asked (recommended name first), even when the
   recommendation looks obvious: user sees them in every list.
5. Remaster, or skill for the Desktop, goes to the folder the user names, `~/Desktop/SKILLS/<name>/` by
   default. Installed copy stays byte for byte, whatever a CONTRIBUTING file, template or reminder says.
6. No attribution to Claude or any AI tool anywhere in the folder, footer and front matter included. Every
   file follows the strip-ai-traces skill, every script the clean-code skill.

## Where it goes

| The skill | Folder |
|---|---|
| holds for one project only | `<repo>/.claude/skills/<name>/` |
| holds for every project of the user | `~/.claude/skills/<name>/` |
| is a remaster or a Desktop skill | the folder the user names |
| is one line of project convention | that project's `CLAUDE.md`, no skill |
| is a lesson from a `/drive` run | `<project>/.ia/skills/<name>/` |

Skill in a project's `.claude/skills` folder is tooling, not committed (the clean-commits skill refuses
it); skill of a skills repository such as claude-skills is committed like any file.

## Lessons

Lesson keeps one fail-then-success for the next agent: a few lines, no test loop. Needs rule 1's written
baseline, rule 6 and a `SKILL.md`, nothing else: writer picks the name without asking, no subagent runs,
no command, tests or README, `check_skill.py` not run on it. Lesson from a `/drive` run uses the template
in `drive-project/worker-brief.md`.

## Folder

`reference/format.md` holds skeletons, naming limits and script conventions.

- `SKILL.md` in English: front matter (`name` = folder name, `description`), a `# Title`, then only what
  the skill needs. Aim 150 lines, 500 is the limit.
- `README.md` in English, for the user, everyday words, never a translation of `SKILL.md`. Skill of the
  claude-skills repository starts it with a line pointing to `INSTALL.md` at the root. May hold
  `## What was tested` or `## Not tested yet`.
- `commands/<command>.md` only when the user starts the skill by hand: English, ASCII only, file name
  included.
- `scripts/` with `tests/test_pure.py`, only where a script checks better than reading (counts, formats,
  parsing, git state). Python 3 called with `python -I`, never crashing.
- `<role>-brief.md` at the root when the skill sends subagents; `reference/*.md` for material only some
  runs need, each named from `SKILL.md` with when to read it.

## Procedure

One skill goes through the whole loop before the next starts. Review runs `check_skill.py` and the
strip-ai-traces `scan.py <folder> --no-git`, reads the skill against the Rules and `reference/format.md`;
no subagent runs unless user asks.

1. Grill: say in one sentence how big the request reads, then ask only what the user alone decides, one
   question at a time (name and command, a real design choice).
2. Classify: folder, what the baseline runs against, failures you expect. Edit: find current version first
   (`<repo>/.ia/skills/<name>/`, `<repo>/.claude/skills/<name>/`, `~/.claude/skills/<name>/`,
   `$CLAUDE_CONFIG_DIR/skills/<name>/`, the plugin cache); not found = question for the user, never a
   baseline against nothing.
3. Build test material following `reference/testing.md`, on data already on disk and current version's own
   examples (sample made up by an agent who knows the traps passes for the wrong reason). Each scenario has
   a checklist of observable results with at least one line splitting old from new.
4. Red: one fresh subagent per scenario, prompt from `subject-brief.md`, never a fork. Record what it chose
   and its excuses word for word. No failure on the real material: stop, tell the user, with the reports.
5. Write the form fitting the failure, nothing for a case no run showed. Subject breaks a rule under
   pressure: prohibition naming the excuse. Right choices, wrong output shape: recipe of the output and its
   parts. Element left out: required slot in the template. Behaviour depends on the case: condition on
   something observable. Avoid "prefer" and "consider" for rules agents skip, and nuance clauses ("unless
   it matters"), which reopen the bargaining.
   Then `python -I "<claude-skills>/writing-skills/scripts/check_skill.py" <folder>` until it refuses nothing.
6. Green: same scenarios with the skill; read each report against the checklist. Each new excuse named and
   forbidden in the rule, its symptom added to the description. Subject that read the skill and still
   failed gets asked why with the follow-up block of `subject-brief.md`. Repeat until nothing new comes up;
   discipline skill ends on a pressure run.
7. Close: write the tested section from the reports; run `check_skill.py` and the strip-ai-traces
   `scan.py <folder> --no-git`; with scripts, the unit tests and the clean-code measure. Delete fixtures,
   check no subagent is left, answer in the user's language: folder, what runs showed, what stays untested.

`check_skill.py` checks front matter, description, size, local links, `README.md`, commands and script
rules, and prints the real paths of itself and of `scan.py`. Its `refused:` lines must go, `check:` lines
get a look, `note:` lines are information only.
