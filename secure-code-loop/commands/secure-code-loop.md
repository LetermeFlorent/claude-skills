---
description: Scan the code with every security scanner found, fix what they report, rescan until clean.
argument-hint: "[scope: files, folder or base revision]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,Agent,SendMessage,AskUserQuestion,WebSearch,WebFetch
---

Scope: $ARGUMENTS. Empty: files changed in the current task, else the whole project.

Load the `secure-code-loop` skill with the `Skill` tool and follow its Procedure.

Final answer in the user's language, as its Report section describes.
