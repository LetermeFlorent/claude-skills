# terse-speech

Agents talk to each other a lot: the main agent sends instructions to helper agents, and each helper sends a report back. Every extra word in those messages is paid for, and long reports fill the main agent's memory, so a long job runs out of room sooner. This skill makes every agent write those messages short: facts only, no titles or bold, no recap, but with code, paths, commands, numbers and every "not" or "only when" kept word for word. Your own replies stay in normal sentences, following your own rules, only shorter. To install it, see `INSTALL.md` at the root of the repository.

The installer adds two hooks, so the skill is always on: one loads it at the start of every session, the other gives it to every helper agent as it starts. There is nothing to type.

## What was tested

Two tasks on a small throwaway shop project, on Sonnet with a Haiku helper. Without the skill, a helper's report came back with headings, bold, the new function pasted again and a side remark about its own command, about 230 words. With the first version of the skill the main agent's instructions got shorter, but the Haiku helper still wrote headings and bold. The rule was then turned into a fixed four-line report shape, and in the next run the Haiku helper answered in those four lines with no headings, bold or pasted code, every fact kept, though each line still carried more explanation than needed. Not tested: the hooks themselves in a live session, a long `/drive` run, and helpers on Opus.
