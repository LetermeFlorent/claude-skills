---
description: Audit a scope against the clean code rules, show the mark out of 20, then fix it.
argument-hint: "[scope: folder, application or file]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,Agent,AskUserQuestion
---

Scope: $ARGUMENTS. Empty: ask for it with `AskUserQuestion`.

Load the `clean-code` skill and follow Audit then Apply. The mark before is shown alone as a heading before any fix. Short final answer: the mark after alone as a heading, then in the user's language steps done with their commit, what is left and why.
