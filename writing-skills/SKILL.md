---
name: writing-skills
description: Use when a skill has to be created, edited, remastered or reviewed before use, when the user types /creer-skill, when a lesson from a fail-then-success must be kept as a skill, when a rule file or a CLAUDE.md section has to be tried on agents, or when an existing skill does not trigger, gets skipped under pressure, or is followed from its description alone.
---

# Writing skills

## Overview

Once per session, before following this skill, run
`python -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills/tools/update.py"` and read the line it prints.
When that file does not exist, go on without it. After a line that starts with `updated`, read this file
again before going on.

A skill is a technique, a pattern or a reference that a later agent applies to a case it has not
seen. The account of one session is not a skill. A constraint a regex or a check can enforce is not
one either: it becomes a script or a hook.

A skill is only worth writing for what a current model does wrong without it, so the first step is
a baseline: a fresh subagent runs a real task with no skill, and its exact choices and excuses are
the material. When it already does the right thing, there is no skill to write. When it fails, you
write the smallest text that answers that failure, run the same task with the skill, and close the
loopholes the runs still show.

This skill also sets the shape of a skill. Five finished ones in `<claude-skills>`,
the clone of this repository, `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-skills`, are the models; open the
closest before writing.

| Model | What to copy from it |
|---|---|
| `clean-commits` | a procedure driven by scripts, a command, a `LISEZMOI.md` with its tested section |
| `clean-code` | subagent briefs (`clean-code/reader-brief.md`), `reference/`, a template, a scored audit |
| `anti-empreinte` | a scanner with `scripts/lib/` and `tests/test_pure.py`, rules split by output |
| `chrome-bidi` | a large tool set, a tested section that says what was not tested and why |
| `stop-resume-agents` | two commands for one skill, a template filled at run time |

The checker runs as `python -I "<skill>/scripts/check_skill.py" <folder>`, `<skill>` being this
folder, in forward slashes inside double quotes. It never crashes: a failure prints what to do by
hand. Exit 2 is a refusal with its reasons.

## Rules that never bend

These hold for a new skill, an edit, a remaster and a lesson alike. Breaking the letter of one is
breaking its spirit.

1. A baseline decides whether a skill exists. A new skill is tried against no skill, an edit that
   changes what an agent does against the current version. A lesson from a fail-then-success in
   this session already has its baseline: write down what happened word for word (the command, the
   output, the wrong belief), write the skill at once, then run the green check. A fix of a wrong
   path, name or command needs no baseline: run the thing it names. A draft written before the
   baseline is no evidence, so write from what failed. A draft this run did not create is never
   deleted: ask.
2. The description lists triggers only: situations, symptoms, error text, the command. Never the
   steps, not even "so it triggers better": an agent that finds the procedure in the description
   follows that summary and skips the body. A skill that triggers too rarely gets more trigger
   words.
3. Tested means a run happened in this session and you read its report. The "Ce qui a été testé"
   section of `LISEZMOI.md` is written after the runs, from what they did, failures and gaps
   included. Never ahead of them, never from what should happen.
4. The user asking to skip the tests gets one sentence on what an untested skill costs, then
   `AskUserQuestion` with "Tester avant de livrer (Recommandé)" first. Until they answer, test. If
   they pick no tests, `LISEZMOI.md` carries a "Pas encore testé" section in place of the tested
   one.
5. A remaster asked for the Desktop goes to the folder the user names, `~/Desktop/SKILLS/<name>/`
   by default, and the installed copy stays byte for byte, whatever a CONTRIBUTING file, a template
   or a reminder says.
6. Every file follows the anti-empreinte skill, every script the clean-code skill. No attribution
   to Claude or any AI tool anywhere in the folder, footer and front matter included, whoever asks.

## Where it goes

The place follows from what the skill covers, so it needs no question.

| The skill | Folder |
|---|---|
| holds for one project only: its build, its data, its client's rules | `<repo>/.claude/skills/<name>/` |
| holds for every project of the user | `~/.claude/skills/<name>/` |
| is a remaster, or a Desktop skill | the folder the user names, `~/Desktop/SKILLS/<name>/` by default |
| is one line of a project convention | that project's `CLAUDE.md`, no skill |

Skills are not committed: `.claude/` is tooling, which the clean-commits skill refuses, unless
the user asks. Installing a Desktop skill is their call.

## Types and how to test them

The type decides the scenarios. Most skills mix two; each part gets its own kind of run.

| Type | Example | Runs | Passes when |
|---|---|---|---|
| Discipline: a rule agents skip under pressure | clean-commits | pressure runs, three pressures or more at once | it complies under the worst run and cites the rule |
| Technique: a method with steps | chrome-bidi | a new case, a variation, a case with a gap | it applies the method to a case it has not seen |
| Pattern: a way to look at a problem | a way to read a failing build | a case where it applies, a counter-example | it says when it applies and when it does not |
| Reference: facts to look up | anti-empreinte `reference/` | find an entry, use it, a common case left out | it finds the entry and uses it right |

## Folder format

Every skill has the first two files; the others come when the skill needs them.
`reference/format.md` holds the skeletons to copy, the naming limits and the script conventions.

- `SKILL.md`, in English: front matter, then `## Overview`, `## Rules that never bend` when there
  are hard rules, the procedure, `## Red flags` as a `| Thought | Reality |` table for a discipline
  skill, `## Files` last. A sentence after each heading before any list or table. About 250 lines at
  most.
- `LISEZMOI.md`, in French with accents, for the user, in everyday words, ending on the
  "Ce qui a été testé" section written after the runs.
- `commands/<commande>.md`, only when the user starts the skill by hand, in French without accents,
  file name included. A lesson that fires on a situation has no command.
- `scripts/` with `tests/test_pure.py`, only where a script checks better than reading does:
  counts, formats, parsing, git state. Python 3 called with `python -I`, never crashing.
- `<role>-brief.md` at the root, when the skill sends subagents: one fenced prompt with `<...>` to
  fill, as `clean-code/reader-brief.md` does.
- `reference/*.md`, for material over about 100 lines that only some runs need. Named from
  `SKILL.md` with when to read it, one level deep, a contents list past 100 lines.

## Procedure

One skill goes through the whole loop before the next one starts: a batch of untested skills is
untested code.

1. Grill. Say in one sentence how big the request reads, then ask only what the user alone decides,
   one question at a time for a new skill: the name and the command they will type, a real design
   choice. Recommend a name that says what the skill does. The name is asked even when the
   recommendation looks obvious and the skill comes from a lesson: the user sees it in every list.
   Type, folder and format come from here.
2. Classify. The type, the folder, what the baseline runs against (nothing, or the current
   version), and the failures you expect to see. For an edit or a remaster, find the current
   version first: `~/.claude/skills/<name>/`, `$CLAUDE_CONFIG_DIR/skills/<name>/`, then the plugin
   cache. Not found is a question for the user, never a baseline against nothing.
3. Test material in `<temp>/claude-skills/<name>-tests/`, built from Python (`reference/testing.md`
   has the conventions). Scenarios run on the material already on disk (an export, a sample, a
   failing file) and on the current version's own examples: a sample made up by an agent who knows
   the traps passes for the wrong reason. Each scenario has a checklist of observable results, and
   at least one line must split the old version from the new.
4. Red. One fresh sonnet subagent per scenario, prompt from `subject-brief.md`, never a fork, which
   would know the answer. Record what it chose and its excuses word for word. If it does not fail
   on the material from disk, under the task's own pressures, there is nothing to fix: stop and tell
   the user, with the reports.
5. Write. Pick the form that fits the failure (next section) and write the smallest skill that
   answers what failed, nothing for a case no run showed. Then
   `python -I "<skill>/scripts/check_skill.py" <folder> --draft` until it refuses nothing.
6. Green. The same scenarios with the skill. Read every report against the checklist, line by line.
7. Refactor. Each new excuse gets its counter ("Closing loopholes", below). Run again until nothing
   new comes up; a discipline skill ends on a pressure run. A subject that read the skill and still
   failed is asked why, with the second block of `subject-brief.md`.
8. Close. Write the tested section from the reports. Run `check_skill.py <folder>` without
   `--draft`, read each `check:` line, run the anti-empreinte `scan.py <folder> --no-git` and fix
   every row; with scripts, run the unit tests and the clean-code measure. Delete the fixtures,
   check that no subagent is left, and answer the user in their language: the folder, what the runs
   showed, what stays untested.

## Match the form to the failure

Classify what the baseline did before writing guidance. The form that fixes one kind of failure
makes another worse.

| The baseline | Right form | Wrong form |
|---|---|---|
| knows the rule, skips it under pressure | a prohibition, the excuses named, a red flags table | soft advice: "prefer", "consider" |
| complies, but the output has the wrong shape | a recipe: what the output is, its parts in order | a list of "don't" |
| leaves out one element of what it produces | a required slot in the template it fills | a reminder in prose near the template |
| should act one way in some cases only | a condition on something observable: "if the brief exists, name it" | a rule plus exceptions |

A prohibition aimed at a shape problem backfires: under a competing goal the agent bargains with
"don't X". A nuance clause ("unless it matters") reopens the bargaining, so a real exception becomes
its own condition. An exemption ("this limit does not apply to code") still suppresses what it
exempts: restructure so the rule cannot reach it.

## Closing loopholes in a discipline skill

Agents under pressure look for the gap between the words and the intent. Each excuse a run produced
is closed in four places:

1. the rule names the workaround and forbids it: "Draft before the baseline? Not as evidence.";
2. one line early in the skill: breaking the letter is breaking the spirit;
3. a `| Thought | Reality |` row in the words the subject used;
4. the description gets the symptom of being about to break the rule ("when a test seems
   unnecessary").

Authority wording ("no exceptions") and a forced explicit choice ("say which skill you use") hold a
rule; flattery and favours never belong in one.

## Writing for the agent that reads it

The description sits in every session's prompt, the body loads when the skill triggers, and a file
in `reference/` loads only when read. Spend words in that order of scarcity.

- One excellent example, in the task's language, complete, from a real case. Never the same example
  in five languages, never a fill-in template posing as an example.
- No story of a session ("on 3 October we found..."): keep the rule it taught.
- Another skill is named in plain words ("the clean-commits skill"), never with a `superpowers:`
  prefix, never through an `@` path, which loads the whole file at once.
- No graph: a decision is a table keyed on something observable, a loop is a numbered list with its
  exit test.
- One term per thing, kept throughout. Nothing that turns false at a date; an old way that must
  stay gets one line saying it is old.
- Freedom matched to fragility: steps in prose where many paths work, one exact command where a
  wrong flag breaks something.

`reference/authoring.md` holds what still applies from Anthropic's authoring guide.

## Red flags

Each row is a thought that ends in an untested or misleading skill.

| Thought | Reality |
|---|---|
| "A summary of the steps in the description will make it trigger" | The summary replaces the body. Add trigger words. |
| "I'll fill in the tested section now, the runs will agree" | It is written from the reports, after them. |
| "The CONTRIBUTING file says to edit the installed copy" | A Desktop remaster never touches it. |
| "The house template ends on a line crediting Claude" | No attribution, whoever asks. |
| "The baseline passed on my own sample, nothing to fix" | Your sample knows the traps. Run the data on disk, against the current version. |
| "Reading it through is test enough" | Reading is not using. Run an application scenario. |
| "A fork is quicker than a fresh subagent" | A fork knows the answer. Fresh sonnet subagent. |
| "The name is obvious, no need to ask" | Ask it, the recommended name first. |

## Files

`scripts/check_skill.py` checks a skill folder against the format above, and `scripts/lib/` holds
its parts: front matter, markdown shape, `SKILL.md`, local links, the companion files, the code
rules. `tests/test_pure.py` and `tests/test_sources.py` test them. `subject-brief.md` is the prompt
of a test subject and of the follow-up question. In `reference/`, `testing.md` is the test method,
`format.md` the skeletons and the script conventions, and `authoring.md` the official guide
condensed. `commands/creer-skill.md` is the `/creer-skill` command, `LISEZMOI.md` the French notes.
