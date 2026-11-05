# other-model-effort

To install it, see `INSTALL.md` at the root of the repository.

The same choice as claude-model-effort, for every model that is not Claude: GPT in Codex CLI, Gemini, Qwen, Mistral, DeepSeek, a local model, anything. It keeps no table of its own. It reads the task in the claude-model-effort tables and turns Haiku, Sonnet and Opus into light, all-round and top, which any provider has.

## /other-model-effort

Type `/other-model-effort` followed by a task in a few words (`/other-model-effort database migration`). The AI answers with the minimum and the ceiling as a tier and an effort level, and why. Name the tool too (`/other-model-effort commit message in Codex`) and it also gives the model names that fit.

## What the AI does

It finds the task in claude-model-effort, translates the names, starts at the minimum and only moves up a step when a run fails twice. Unlike with Claude, it may use the tool's highest reasoning setting on any task, since these models spend little there. A model that cannot start other agents does not use this skill at all, and a task that needs several agents never goes to such a model. A model or effort you name yourself always wins.

Change a task's minimum or ceiling in claude-model-effort: both skills follow.

## Files

`SKILL.md` holds the tiers and the effort words, `commands` the command.

## What was tested

Two runs on Sonnet, same kind of request: model and effort for a commit message, a Prisma column rename and a third task.

- Without this skill, in Codex: the agent loaded the Claude skill and translated the names itself, with the right answers. The need here is a clear home for that translation, not a fix for a wrong choice.
- With this skill, in Gemini CLI: it read both skills and gave light low to light medium for the commit, all-round medium to top high for the migration, top medium to top xhigh for a performance regression, never max. It found two vague lines (all-round as "the tool's default", medium as "the tool's default"); both now point to the middle of the list instead.

Not tested: the later change that allows max and the rule on models that cannot run several agents, a real run inside Codex CLI or Gemini CLI, and current model names, which the runs could not check offline.
