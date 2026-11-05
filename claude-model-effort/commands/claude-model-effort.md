---
description: Tell which Claude model and effort level to use for a task, from the cheapest that works to the ceiling.
argument-hint: "<task in a few words>"
allowed-tools: Read,Skill
---

Task: $ARGUMENTS. Empty: give the rules of the skill in three lines.

Load the `claude-model-effort` skill and follow its `/claude-model-effort <task>` part. Short answer in the user's language: minimum, ceiling, why.
