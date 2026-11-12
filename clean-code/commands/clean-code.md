---
description: Audit a scope against the clean code rules, show the note out of 20, then fix it.
argument-hint: "[scope: folder, application or file]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,Agent,AskUserQuestion
---

Scope: $ARGUMENTS. Empty: ask for it with `AskUserQuestion`.

Load the `clean-code` skill and follow Audit then Apply, then give the final answer its Report section describes.
