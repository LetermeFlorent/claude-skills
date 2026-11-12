---
description: Take a goal on this project to pushed commits: questions first, then a silent run showing only a percentage.
argument-hint: "<goal in a few words>"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,AskUserQuestion,Agent,SendMessage
---

Goal: $ARGUMENTS. Empty: run the skill's step 1 first, which resumes an unfinished plan; with none to resume, ask only for the goal, in one plain line, then go on with step 2.

Load the `drive-project` skill with the `Skill` tool and follow its procedure. You are the lead: every task goes to a subagent, never done by you.

After the questions, every message is a percentage only; the last one is `100%` and five words at most, in the user's language.
