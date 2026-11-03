---
description: Create an isolated git worktree on its own branch, then run the baseline tests.
argument-hint: "[task in a few words, optional start branch]"
allowed-tools: Read,Write,Bash,Grep,Glob,Skill,AskUserQuestion,EnterWorktree
---

Details: $ARGUMENTS. They name the task (so the branch and the folder) and a start branch when they cite one. Empty: work from the conversation, and ask one question only if the task stays unknown.

Load the `using-git-worktrees` skill with the `Skill` tool and follow its procedure.

Short final answer in the user's language: path, branch and start point, changes left in the original folder, baseline test result.
