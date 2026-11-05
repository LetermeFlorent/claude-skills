---
name: other-model-effort
description: Use when the user types /other-model-effort, when about to start an agent, a subagent or a run on a model that is not Claude, in any tool, and its model or reasoning effort must be picked, when such a run seems to need a stronger or a cheaper model, or when a task with several agents is about to go to a model that is not Claude.
---

# Picking a model and an effort level outside Claude

Only a model that can start subagents and follow them uses this skill. A model that cannot (its tool has no
subagent or task feature, or it loses track of tool calls over a long run) ignores this skill entirely and
does its own task alone.

The task tables live in one place, the claude-model-effort skill (`../claude-model-effort/SKILL.md`, next to
this folder). Read the row for the task there, then translate its Claude names into the three tiers below.
Never pick a model or an effort for these tools from habit or from the tool's default: the row decides.

## Tiers

Every provider sells a light, an all-round and a top model. Price and speed tell them apart, never a name.

| Claude name in the table | Tier | How to spot it in any provider's list |
|---|---|---|
| Haiku | light | the cheapest and fastest of the provider's list |
| Sonnet | all-round | the middle of the provider's price list, even when the tool starts on another model by default |
| Opus | top | the provider's strongest reasoning model, the most expensive of the list |

A provider with two tiers only: a missing light tier becomes all-round, a missing top tier becomes all-round
one effort step higher. A local model runs as light, whatever its
name, unless the user says otherwise.

## Effort

The table's effort words map onto whatever the tool calls its reasoning setting (effort, thinking level,
reasoning budget).

| Table | In the tool |
|---|---|
| low | the lowest setting that still reasons |
| medium | the middle setting of the tool's list, whatever its default is |
| high | one step above medium |
| xhigh | the highest setting below max, unlimited or unbounded |
| max | the tool's max, unlimited or unbounded setting |

Unlike Claude, these models may run at max on any task: their highest setting costs little. The table's effort
is where a run starts, and any run may go up to max. The tier still stays between the minimum and the
ceiling. A tool or model with no reasoning setting (often the light tier) takes the tier alone and drops the
effort.

## Several agents

A task that needs several agents at once (a long agentic task, a large feature split across agents, a
workflow) never goes to a model that cannot run them: it goes to a model that can, or to Claude.

## Rules

Rules 2, 4, 5 and 6 of claude-model-effort hold here: effort sets depth and not quality, the user's choice
wins, the highest minimum wins for mixed tasks, two failures move up one step (effort first, up to max, then
the tier, never past the ceiling's tier). Rule 1 does not hold: max is allowed. Rule 3 becomes: set the
model and the effort where the tool takes them (its command-line flags, its config file, the agent
definition), on the run itself, never as a global default the user did not ask for.

## /other-model-effort <task>

Find the row in claude-model-effort as its `/claude-model-effort <task>` part says, then answer in the
user's language with the minimum and the ceiling written as tier and effort (`all-round medium`, `top
high`), and the reason, in two or three lines. Never name a model of any provider: the
tier is the answer. When the task needs several agents, say whether that model can
run them.
