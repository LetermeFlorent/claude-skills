# Reader brief

Sent as the prompt of one reader agent when the scope holds more than `reader_threshold` code
files (150 by default). `measure.py` prints the folder batches as `reader 1: ...` lines, one agent
per batch, `readers` at most (4 by default), launched in the same message so they run side by
side. Fill every `<...>` and send the block as is.

`````text
You are reader <n> of a clean-code audit. The audit is read-only: you edit no file, rename nothing,
move nothing, install nothing, build nothing that writes to disk, and run no git command other than
log, show, diff, blame, grep and ls-files.

Project root: <absolute project root>
Run folder: <absolute path of .ia/clean-code/<run>>
Your folders, and only these: <folders from the reader line>
Rules: <absolute path of the skill>/SKILL.md, section "The rules". Read it first.

measure.py already flagged what a script can see. List those candidates for your folders with:
python -I "<skill>/scripts/findings.py" --run "<run folder>" list
Do not judge them: a separate verifier does. Your job is what a script cannot see, by reading
every code file in your folders, test files included:
- rule 2, a file mixing several jobs: name each job and its line range;
- rule 5, duplication: both locations, file and line, and what is repeated;
- rule 6, a function whose job is split badly even under the limits;
- rule 7, names that lie about what they hold, or the same thing named two ways;
- rule 8, mutation of shared state, an error turned into a default value without a trace;
- rule 9, public behaviour with no test going through the public API;
- rule 11, code or assets only dev needs that the production build still ships;
- rule 16, a variable that could be removed, inlined, narrowed or made constant;
- rule 0, a bad practice outside the grid, with its weight from 0.5 to 3 points.

Add each finding once, with its proof:
python -I "<skill>/scripts/findings.py" --run "<run folder>" add --rule <n> --file <path from root>
  --line <n> --what "<the defect, short>" --proof "<the quoted line, or both locations>"
  --source reader-<n>
Rule 0 also takes --points. A finding the script already holds is refused with its id: leave it.
Several readers write at once; the script locks the file, so a refusal on a lock means retry once.

A finding without a file, a line and a quoted proof is a guess: drop it. Framework conventions
(a Next.js routes folder, a NestJS module folder, generated code) are not defects.

Finish with this block and nothing after it:
READER REPORT <n>
files read: <count>
added: <ids, or none>
per rule: 2 <count>, 5 <count>, 6 <count>, 7 <count>, 8 <count>, 9 <count>, 11 <count>, 16 <count>, 0 <count>
not read, and why: <files skipped, or none>
`````
