---
description: Take a goal on this project to pushed commits: questions first, then a silent run showing only a percentage.
argument-hint: "<goal in a few words>"
allowed-tools: Read,Write,Edit,Bash,Glob,Skill,AskUserQuestion,Agent,SendMessage,ToolSearch
---

Goal: $ARGUMENTS. Empty: run skill's step 1 first, which resumes an unfinished plan; none to resume: ask only for goal, one plain line, then go on with step 2.

Load `drive-project` skill with `Skill` tool, follow its procedure. You are lead: every task goes to a subagent, never done by you.

After questions every message is a percentage only; last one is `100%` and five words at most, in user's language.
