---
description: Commit this session's files cleanly, one commit per intent, then push the branch.
argument-hint: "[files, folder or intent to commit]"
allowed-tools: Read,Write,Bash,Grep,Glob,Skill,AskUserQuestion
---

Load `clean-commits` skill, follow its procedure in `/commit` mode. Details: $ARGUMENTS. Not empty: they narrow files or steer message, never add file from another session without asking. Short final answer in user's language: each commit (hash, title), push, files left out and why.
