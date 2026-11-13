---
description: Audit a scope against the clean code rules, show the note out of 20, then fix it.
argument-hint: "[scope: folder, application or file]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,Agent,AskUserQuestion
---

Scope: $ARGUMENTS. Empty: ask for it with `AskUserQuestion`.

Load `clean-code` skill, follow Audit then Apply, then give final answer its Report section describes.
