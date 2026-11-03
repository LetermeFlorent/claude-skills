---
description: Audit a scope against the clean code rules, give a mark out of 20, then ask what to fix.
argument-hint: "[scope: folder, application or file]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,Agent,AskUserQuestion
---

Scope: $ARGUMENTS. Empty: ask for it with `AskUserQuestion`.

Load the `clean-code` skill and follow Audit then Apply. Short final answer in the user's language: mark before and after, steps done with their commit, what is left and why.
