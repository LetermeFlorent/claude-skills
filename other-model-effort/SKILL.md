---
name: other-model-effort
description: Use when the user types /other-model-effort, when about to start an agent, a subagent or a run on a model that is not Claude (Codex CLI, Gemini CLI, Qwen Code, OpenCode or any other tool and provider) and its model or reasoning effort must be picked, or when such a run seems to need a stronger or a cheaper model.
---

# Picking a model and an effort level outside Claude

The task tables live in one place, the claude-model-effort skill (`../claude-model-effort/SKILL.md`, next to
this folder). Read the row for the task there, then translate its Claude names into the three tiers below.
Never pick a model or an effort for these tools from habit or from the tool's default: the row decides.

## Tiers

Every provider sells a light, an all-round and a top model. The words in their names tell them apart.

| Claude name in the table | Tier | How to spot it in any provider's list |
|---|---|---|
| Haiku | light | the cheapest and fastest: names with mini, nano, flash, lite, small, fast, or the fewest parameters |
| Sonnet | all-round | the middle of the provider's price list, even when the tool starts on another model by default |
| Opus | top | the provider's strongest reasoning model: names with pro, max, ultra, large, thinking, or the highest price |

A provider with two tiers only: a missing light tier becomes all-round, a missing top tier becomes all-round
one effort step higher, still never past the ceiling's effort. A local model runs as light, whatever its
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

Never the tool's max, unlimited or unbounded setting. A tool or model with no reasoning setting (often the
light tier) takes the tier alone and drops the effort.

## Rules

Rules 1, 2, 4, 5 and 6 of claude-model-effort hold here unchanged: no max, effort sets depth and not
quality, the user's choice wins, the highest minimum wins for mixed tasks, two failures move up one step and
never past the ceiling. Rule 3 becomes: set the model and the effort where the tool takes them (its
command-line flags, its config file, the agent definition), on the run itself, never as a global default
the user did not ask for.

## /other-model-effort <task>

Find the row in claude-model-effort as its `/claude-model-effort <task>` part says, then answer in the
user's language with the minimum and the ceiling written as tier and effort (`all-round medium`, `top
high`), and the reason, in two or three lines. When the user names the tool or the provider, add the model
names of that provider that fit each tier. Never answer max.
