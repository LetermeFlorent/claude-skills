---
description: Commit this session's files cleanly, one commit per intent, then push the branch.
argument-hint: "[files, folder or intent to commit]"
allowed-tools: Read,Write,Bash,Grep,Glob,Skill,AskUserQuestion
---

Load the `clean-commits` skill and follow its procedure in `/commit` mode. Details: $ARGUMENTS. When not empty, they narrow the files or steer the message, never adding a file from another session without asking. Short final answer in the user's language: each commit (hash, title), the push, the files left out and why.
