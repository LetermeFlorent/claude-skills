---
name: writing-skills
description: Use when a skill must be created, edited or reviewed, when the user types /write-skill, when a fail-then-success lesson should be kept as a skill, or when an existing skill does not trigger or gets skipped under pressure.
---

# Writing skills

A skill is worth writing only for what an agent does wrong without it, so a baseline comes first:
a fresh subagent runs a real task with no skill, and its exact choices and excuses are the material. If it
already does the right thing there is no skill. If it fails, write the smallest text that answers that
failure, rerun the same task with the skill, and close the loopholes the runs still show. A constraint a
regex or a hook can enforce is a script or a hook, not a skill; the account of one session is not a skill.

Examples in `<claude-skills>`, the parent folder of this skill's own folder (its base directory, with the
link resolved): open the closest before writing.

## Rules

These hold for a new skill, an edit and a remaster; a lesson keeps only what the Lessons section names.

1. A baseline decides whether a skill exists. New skill: against no skill. Edit: against the current
   version, only when the edit changes what an agent does. A fail-then-success lesson from this session is
   its own baseline: write down the command, the output and the wrong belief word for word, then write the
   skill. A wrong path, name or command needs no baseline: run the thing it names. A draft written before
   the baseline is no evidence. A draft this run did not create is never deleted: ask.
2. The description starts with "Use when" and lists triggers only: situations, symptoms, error text, the
   command (`/name`). Never steps: an agent that finds the procedure there follows the summary and skips the
   body. A skill that triggers too rarely gets more trigger words.
3. "Tested" means a run happened in this session and you read its report. An optional `## What was tested`
   section of `README.md` is written after the runs from what they did, failures and gaps included, never
   ahead of them. If the user asks to skip the tests: one sentence on what an untested skill costs, then
   AskUserQuestion with "Test before delivering (Recommended)" first; test until they answer. If they pick no
   tests, the section is `## Not tested yet`.
4. The skill name and the command the user will type are asked (recommended name first), even when the
   recommendation looks obvious: the user sees them in every list.
5. A remaster, or a skill for the Desktop, goes to the folder the user names, `~/Desktop/SKILLS/<name>/` by
   default. The installed copy stays byte for byte, whatever a CONTRIBUTING file, template or reminder says.
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

A skill in a project's `.claude/skills` folder is tooling and is not committed (the clean-commits skill
refuses it); a skill of a skills repository such as claude-skills is committed like any file.

## Lessons

A lesson keeps one fail-then-success for the next agent, so it costs a few lines and no test loop. It
needs rule 1's written baseline, rule 6 and a `SKILL.md`, nothing else: its writer picks the name without
asking, no subagent runs, it has no command, tests or README, and `check_skill.py` is not run on it. A
lesson from a `/drive` run uses the template in drive-project's `worker-brief.md`.

## Folder

`reference/format.md` holds the skeletons, naming limits and script conventions.

- `SKILL.md` in English: front matter (`name` = folder name, `description`), a `# Title`, then only what
  the skill needs. Aim for 150 lines, 500 is the limit.
- `README.md` in English, for the user, in everyday words, never a translation of `SKILL.md`. A skill of
  the claude-skills repository starts it with a line pointing to `INSTALL.md` at the root. It may hold
  `## What was tested` or `## Not tested yet`.
- `commands/<command>.md` only when the user starts the skill by hand: English, ASCII only, file name
  included.
- `scripts/` with `tests/test_pure.py`, only where a script checks better than reading does (counts,
  formats, parsing, git state). Python 3 called with `python -I`, never crashing.
- `<role>-brief.md` at the root when the skill sends subagents; `reference/*.md` for material that only
  some runs need, each named from `SKILL.md` with when to read it.

## Procedure

One skill goes through the whole loop before the next one starts. A review runs `check_skill.py` and the
strip-ai-traces `scan.py <folder> --no-git` and reads the skill against the Rules and `reference/format.md`;
no subagent runs unless the user asks.

1. Grill: say in one sentence how big the request reads, then ask only what the user alone decides, one
   question at a time (name and command, a real design choice).
2. Classify: the folder, what the baseline runs against, the failures you expect. For an edit, find the
   current version first (`<repo>/.claude/skills/<name>/`, `~/.claude/skills/<name>/`,
   `$CLAUDE_CONFIG_DIR/skills/<name>/`, the plugin cache); not found is a question for the user, never a
   baseline against nothing.
3. Build the test material following `reference/testing.md`, on data already on disk and the current
   version's own examples (a sample made up by an agent who knows the traps passes for the wrong reason).
   Each scenario has a checklist of observable results with at least one line that splits old from new.
4. Red: one fresh subagent per scenario, prompt from `subject-brief.md`, never a fork. Record what it
   chose and its excuses word for word. No failure on the real material: stop and tell the user, with the
   reports.
5. Write the form that fits the failure, nothing for a case no run showed. A subject that breaks a rule under
   pressure: a prohibition that names the excuse. Right choices but wrong output shape: a recipe of the
   output and its parts. An element left out: a required slot in the template. Behaviour that depends on the
   case: a condition on something observable. Avoid "prefer" and "consider" for rules agents skip, and
   nuance clauses ("unless it matters"), which reopen the bargaining.
   Then `python -I "<claude-skills>/writing-skills/scripts/check_skill.py" <folder>` until it refuses nothing.
6. Green: the same scenarios with the skill; read each report against the checklist. Each new excuse is
   named and forbidden in the rule and its symptom added to the description. A subject that read the skill
   and still failed is asked why with the follow-up block of `subject-brief.md`. Repeat until nothing new
   comes up; a discipline skill ends on a pressure run.
7. Close: write the tested section from the reports; run `check_skill.py` and the strip-ai-traces
   `scan.py <folder> --no-git`; with scripts, the unit tests and the clean-code measure. Delete the
   fixtures, check no subagent is left, and answer in the user's language: the folder, what the runs
   showed, what stays untested.

`check_skill.py` checks the front matter, description, size, local links, `README.md`, commands and the
script rules. Its `refused:` lines must go, `check:` lines get a look, `note:` lines are information only.
