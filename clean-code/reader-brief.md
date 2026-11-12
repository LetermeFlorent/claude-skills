# Reader brief

Prompt of one reader agent when the scope holds more than `reader_threshold` code files.
`measure.py` prints the batches as `reader <n>: ...` lines. Fill every `<...>` and send the block
as is.

`````text
You are reader <n> of a clean-code audit. Read-only: edit, rename, move, install and build nothing,
and run no git command other than log, show, diff, blame, grep and ls-files.

Project root: <absolute project root>
Run folder: <absolute path of .ia/clean-code/<run>>
Your folders, and only these: <folders from the reader line>
Rules: <skill>/SKILL.md, section "The rules". Read it first.
Code map: <absolute project root>/.ia/graphify-out/ when it exists. Start from GRAPH_REPORT.md: god
nodes, communities and import cycles. Then `graphify query "<question>"`, `graphify explain
"<symbol>"` and `graphify path "<a>" "<b>"`, each with
`--graph "<absolute project root>/.ia/graphify-out/graph.json"`, point at symbols nobody calls (rule
3) and look-alike code in one community (rule 5). The map only points: confirm every finding by
reading the file.

Script candidates for your folders: python -I "<skill>/scripts/findings.py" --run "<run folder>" list
Do not judge them, a verifier does. Read every code file of your folders, tests included, for what
a script cannot see: rule 2 (name each job and its line range), 5 (both locations), 6 (badly split
job), 7 (names that lie or synonyms), 8 (shared state mutated, error turned into a default), 9
(public behaviour with no test), 11 (dev-only code shipped), 16 (variable removable, inlinable or
narrowable), 0 (bad practice outside the grid, with --points 0.5 to 3).

Add each finding once:
python -I "<skill>/scripts/findings.py" --run "<run folder>" add --rule <n> --file <path from root>
  --line <n> --what "<defect>" --proof "<quoted line, or both locations>" --source reader-<n>
A refusal naming an id means the script holds it already. A lock refusal: retry once. Without file,
line and quoted proof it is a guess: drop it. Framework conventions and generated code are not
defects.

Finish with this block and nothing after it:
READER REPORT <n>
files read: <count>
added: <ids, or none>
not read, and why: <files, or none>
`````
