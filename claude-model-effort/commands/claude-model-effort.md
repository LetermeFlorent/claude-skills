---
description: Tell which Claude model and effort level to use for a task, from the cheapest that works to the ceiling.
argument-hint: "<task in a few words>"
allowed-tools: Read,Skill
---

Task: $ARGUMENTS. Empty: give skill rules in three lines.

Load `claude-model-effort` skill, follow its `/claude-model-effort <task>` part. Short answer in user's language: minimum, ceiling, why.
