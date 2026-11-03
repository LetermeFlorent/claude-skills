---
description: Find and remove traces of AI generation from a file, a folder or a repository.
argument-hint: "[file, folder or repository]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,AskUserQuestion
---

Load the `strip-ai-traces` skill and follow its `/strip-ai-traces <target>` part. Target: $ARGUMENTS, or the current folder when empty (say so). Short final answer in the user's language: one line per fix, then what is left with file and line.
