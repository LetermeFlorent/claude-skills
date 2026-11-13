---
description: Create an isolated git worktree on its own branch, then run the baseline tests.
argument-hint: "[task in a few words, optional start branch]"
allowed-tools: Read,Write,Bash,Grep,Glob,Skill,AskUserQuestion,EnterWorktree
---

Details: $ARGUMENTS. They name task (so branch and folder) and start branch when they cite one. Empty: work from conversation, ask one question only if task stays unknown.

Load `using-git-worktrees` skill with `Skill` tool, follow its procedure.

Short final answer in user's language: path, branch and start point, changes left in original folder, baseline test result.
