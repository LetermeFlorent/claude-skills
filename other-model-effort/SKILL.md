---
name: other-model-effort
description: Use when user types /other-model-effort, before starting an agent, subagent or run on a model that is not Claude, in any tool, whose model or reasoning effort must be picked, when such a run seems to need a stronger or cheaper model, or when a task with several agents is about to go to a model that is not Claude.
---

# Picking a model and an effort level outside Claude

/other-model-effort command always gets its answer. Rest of skill only for a model that can start subagents
and follow them. Model that cannot (tool has no subagent or task feature, or it loses track of tool calls
over long run) ignores skill, does own task alone.

Task tables live in one place, claude-model-effort skill (`../claude-model-effort/SKILL.md`, next to this
folder). Read task row there, translate its Claude names into three tiers below. Never pick model or effort
for these tools from habit or tool default: row decides.

## Tiers

Every provider sells light, all-round and top model. Price and speed tell them apart, never a name.

| Claude name in the table | Tier | How to spot it in any provider's list |
|---|---|---|
| Haiku | light | cheapest and fastest of provider's list |
| Sonnet | all-round | middle of provider's price list, even when tool starts on another model by default |
| Opus | top | provider's strongest reasoning model, most expensive of list |

Provider with two tiers only: missing light tier becomes all-round, missing top tier becomes all-round one
effort step higher. Local model runs as light, whatever its name, unless user says otherwise.

## Effort

Table effort words map onto whatever tool calls its reasoning setting (effort, thinking level, reasoning
budget).

| Table | In the tool |
|---|---|
| low | lowest setting that still reasons |
| medium | middle setting of tool's list, whatever its default |
| high | one step above medium |
| xhigh | highest setting below max, unlimited or unbounded |
| max | tool's max, unlimited or unbounded setting |

Unlike Claude, these models may run at max on any task: highest setting costs little. Table effort is where
run starts; any run may go up to max. Tier still stays between minimum and ceiling. Tool or model with no
reasoning setting (often light tier) takes tier alone, drops effort.

## Several agents

Task needing several agents at once (long agentic task, large feature split across agents, workflow) never
goes to a model that cannot run them: goes to a model that can, or to Claude.

## Rules

Rules 2, 4, 5, 6 and 7 of claude-model-effort hold here: effort sets depth not quality, user's choice wins,
highest minimum and highest ceiling win for mixed tasks, two failures move up one step (effort one level at a
time up to max, then next tier at minimum's effort, never past ceiling's tier), task with no row takes
closest row, named next to setting. Rule 1 does not hold: max allowed. Rule 3 becomes: set model and effort
where tool takes them (command-line flags, config file, agent definition), on run itself, never as global
default user did not ask for.

## /other-model-effort <task>

Find row in claude-model-effort as its `/claude-model-effort <task>` part says, answer in user's language
with minimum and ceiling as tier and effort (`all-round medium`, `top high`), and reason, two or three lines.
Never name a model of any provider: tier is the answer. Task needs several agents: say whether that model
can run them.
