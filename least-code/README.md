# least-code

Agents tend to write more code than a task needs: an extra option "for later", a helper that already exists written again, a new library for three lines. They also tend to read and search more than they need once the answer is found. This skill makes them do the smallest change that fully solves the task, reuse what the project already has, skip what nobody asked for, and stop searching once they know enough. It never cuts tests, checks, security or anything you asked for. When something was skipped on purpose, the agent says so in one line at the end instead of leaving a note in the code. To install it, see `INSTALL.md` at the root of the repository.

The installer adds two hooks, so the skill is always on: one loads it at the start of every session, the other gives it to every helper agent as it starts. There is nothing to type. It replaces Ponytail, which the repository used to install.

## What was tested

One task on a small throwaway shop project, on Sonnet: a failing price test, with a note from the client asking to "keep it flexible" for other currencies. With Ponytail still loaded and with this skill, the agent reused the existing number helper in one line and added no currency option; with this skill its reply was shorter and named the currency limit as a known shortcut. A second task, handed to a Haiku helper, also reused the existing function. Not tested: a task without Ponytail loaded at all, the hooks in a live session, and large refactors.
