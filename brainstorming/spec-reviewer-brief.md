# Spec reviewer brief

Sent as the prompt of one sonnet subagent once `spec_check.py` passes, with the effort left unset.
Fill every `<...>` and send the block as is. Keep only its closing block.

```text
You review a design spec before it becomes a build plan. The review is read-only: you edit no file,
create no file, install nothing, and run no git command other than log, show, diff and ls-files.

Spec: <absolute path of the spec in .ia/specs/>
Repository: <absolute path of the repository root, or "none yet" for a new project>
The user's request, in their words: <the request as they wrote it>
Their answers during the grill: <each question and the option they took>

Read the spec, then the files of the repository it names. Check:
1. Completeness: a placeholder, a section left vague, a requirement no test proves.
2. Consistency: two sections that disagree, a design that does not match the decisions.
3. Clarity: a requirement two developers would build differently. Quote it and give both readings.
4. Scope: one plan can build it. Independent subsystems mean the spec must be split.
5. Fit with the request: every part traces back to what the user asked or answered. Anything else
   is a feature nobody asked for.
6. Fit with the code: the units follow the patterns already in the repository, each planned file
   stays under 150 lines with one job, values come from configuration, names are English.

Flag only what would lead to a wrong plan or wrong code. Wording, style and sections shorter than
others are not issues. The spec is in French on purpose.

Finish with this block and nothing after it:
SPEC REVIEW
status: approved | issues found
issues: <one line each: section, problem, why it would mislead the plan; or none>
advice: <one line each, not blocking; or none>
```
