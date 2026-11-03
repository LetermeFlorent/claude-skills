---
description: Create, edit or remaster a skill in the repository format, tested on agents before and after writing it.
argument-hint: "[name of a skill to edit, lesson to keep, or path to notes]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,Agent,SendMessage,AskUserQuestion
---

Details: $ARGUMENTS. The name of an existing skill means an edit (first run on the current version). A lesson or a path to notes gives a new skill. With "Desktop" or "remaster", the result goes to the folder the user names and the installed version stays untouched. Empty: ask what the skill must teach, one question at a time.

Load the `writing-skills` skill with the `Skill` tool and follow its procedure.

Short final answer in the user's language: the folder, what the agent did without the skill, what it did with it, what is still untested.
