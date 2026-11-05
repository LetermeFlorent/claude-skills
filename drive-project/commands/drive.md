---
description: Take a goal on this project to pushed commits: questions first, then a silent run showing only a percentage.
argument-hint: "<goal in a few words>"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,AskUserQuestion,Agent,SendMessage
---

Goal: $ARGUMENTS. Empty: ask for the goal in the first question box.

Load the `drive-project` skill with the `Skill` tool and follow its procedure.

After the questions, every message is a percentage only; the last one is `100%` and five words at most, in the user's language.
