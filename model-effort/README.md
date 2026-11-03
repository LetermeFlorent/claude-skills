# model-effort

Each agent the AI starts can run on a light, an all-round or a deep model, at an effort level from low to max. This skill tells it which pair to use for each kind of task: a minimum that does the job for the fewest tokens, and a ceiling it never goes past. To install it, see `INSTALL.md` at the root of the repository.

## /model-effort

Type `/model-effort` followed by a task in a few words (`/model-effort database migration`). The AI answers with the minimum, the ceiling and why.

## What the AI does

Before starting an agent, it finds the task in the tables of `SKILL.md`, starts at the minimum and only moves up a step when a run fails twice. It never uses the max effort level. A model or effort you name yourself always wins.

This is the only skill that names models and effort levels: the others leave them out on purpose, so the choice lives in one place.

## Files

`SKILL.md` holds the rules and the tables, `commands` the command.
