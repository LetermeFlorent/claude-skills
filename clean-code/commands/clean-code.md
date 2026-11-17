---
description: Audit a scope against the clean code rules, show the note out of 100, then fix it.
argument-hint: "[scope: folder, application or file] [passes: 1 to 3, or until <note>]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,Agent,AskUserQuestion
---

Scope and passes: $ARGUMENTS. Either missing: ask for it with `AskUserQuestion`.

Load `clean-code` skill, follow Audit then Apply, then give final answer its Report section describes.
