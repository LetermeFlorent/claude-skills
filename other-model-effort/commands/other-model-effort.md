---
description: Tell which model tier and effort level to use for a task on a model that is not Claude.
argument-hint: "<task in a few words>"
allowed-tools: Read,Skill
---

Task: $ARGUMENTS. Empty: give skill tiers and rules in three lines.

Load `other-model-effort` skill, follow its `/other-model-effort <task>` part. Short answer in user's language: minimum, ceiling, why, and whether model can run several agents when task needs them.
