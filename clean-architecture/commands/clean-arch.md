---
description: Audit a scope's folder layout, show the note out of 20, then reorganise it.
argument-hint: "[scope: folder or application]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,Agent,SendMessage,AskUserQuestion
---

Scope: $ARGUMENTS. Empty: ask for it with `AskUserQuestion`.

Load the `clean-architecture` skill with the `Skill` tool and follow Audit then Apply.

Final answer in the user's language, as its Report section describes.
