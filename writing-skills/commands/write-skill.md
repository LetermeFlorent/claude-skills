---
description: Create, edit or remaster a skill in the repository format, tested on agents before and after writing it.
argument-hint: "[name of a skill to edit, lesson to keep, or path to notes]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob,Skill,Agent,SendMessage,AskUserQuestion
---

Details: $ARGUMENTS. Name of an existing skill = edit (first run on current version). Lesson or path to notes = new skill. With "Desktop" or "remaster", result goes to the folder the user names, installed version untouched. Empty: ask what the skill must teach, one question at a time.

Load the `writing-skills` skill with the `Skill` tool, follow its procedure.

Short final answer in user's language: folder, what the agent did without the skill, what it did with it, what is still untested.
