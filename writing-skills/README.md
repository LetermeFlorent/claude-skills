# writing-skills

A skill and a command to write, fix or remaster the other skills. To install them, see `INSTALL.md` at the root of the repository.

## /write-skill

Type `/write-skill` followed by what the skill should teach. Claude first gives a real task to an agent that does not have the skill, to see where it goes wrong: if it succeeds alone, there is nothing to write and Claude tells you so. Otherwise it writes the shortest skill that fixes those mistakes, reruns the same trial with it and plugs the remaining gaps. A skill that enforces a rule also goes through a pressure trial (tight deadline, work already done, an instruction that pushes towards cheating).

The argument changes the starting point. `/write-skill clean-commits` edits an existing skill, the first trial runs on the current version. A lesson, or the path of a notes file, gives a new skill. With "Desktop" or "remaster", the result goes in the folder you name (`~/Desktop/SKILLS/<name>/` by default) and the installed version is not touched. After a failure followed by a success, the failure you lived counts as the first trial.

Claude asks you for the name of the skill and the name of the command, with its suggestion first. If you ask to skip the trials, it says in one sentence what an untested skill costs and lets you choose. A skill specific to a project goes in the project's `.claude/skills/`, a skill that applies everywhere in `~/.claude/skills/`. A project skill in `.claude/skills/` stays out of git; a skill of this repository is committed like any other file.

## What is in the folder

`SKILL.md` holds the method. `scripts/check_skill.py` checks that a skill folder follows the format (header, description, README, command, script rules). `subject-brief.md` is the brief of a test agent. `reference/` holds the trial method and the file skeletons. `tests` covers the checker.
