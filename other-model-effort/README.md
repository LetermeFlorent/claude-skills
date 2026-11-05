# other-model-effort

To install it, see `INSTALL.md` at the root of the repository.

The same choice as claude-model-effort, for every model that is not Claude, in any tool, a local one included. It keeps no table of its own. It reads the task in the claude-model-effort tables and turns Haiku, Sonnet and Opus into light, all-round and top, which any provider has.

## /other-model-effort

Type `/other-model-effort` followed by a task in a few words (`/other-model-effort database migration`). The AI answers with the minimum and the ceiling as a tier and an effort level, and why. It never names a model: the tier is the answer.

## What the AI does

It finds the task in claude-model-effort, translates the names, starts at the minimum and only moves up a step when a run fails twice. Unlike with Claude, it may use the tool's highest reasoning setting on any task, since these models spend little there. A model that cannot start other agents does not use this skill at all, and a task that needs several agents never goes to such a model. A model or effort you name yourself always wins.

Change a task's minimum or ceiling in claude-model-effort: both skills follow.

## Files

`SKILL.md` holds the tiers and the effort words, `commands` the command.

## What was tested

Three runs on Sonnet, in tools that are not Claude.

- Without this skill: the agent loaded the Claude skill and translated the names itself, with the right answers. The need here is a clear home for that translation, not a fix for a wrong choice.
- With the first version: right tiers and efforts for a commit message, a column rename and a performance regression. It found two vague lines on the tool's default; both now point to the middle of the list.
- With max allowed and the subagent rule: it started a regression hunt at top medium and allowed effort up to max, refused to hand a five-agent job to a model with no subagent feature, and said such a model ignores the skill. It found one line still capping effort at the ceiling, now removed.

Not tested: a real run inside another tool than Claude Code, and the version without any model name.
