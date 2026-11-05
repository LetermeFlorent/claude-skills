---
description: Tell which model tier and effort level to use for a task on a model that is not Claude.
argument-hint: "<task in a few words> [tool or provider]"
allowed-tools: Read,Skill
---

Task: $ARGUMENTS. Empty: give the tiers and the rules of the skill in three lines.

Load the `other-model-effort` skill and follow its `/other-model-effort <task>` part. Short answer in the user's language: minimum, ceiling, why.
