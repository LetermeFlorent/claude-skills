# Verifier brief

Prompt of one fresh agent once every candidate is in findings.json. Fill every `<...>`, send block as is.

`````text
You verify candidates of a clean-architecture audit. Read-only: edit nothing, run nothing that writes,
apart from findings.py below. You are told to refute: confirm only what survives.

Project root: <absolute project root>
Run folder: <absolute path of .ia/clean-architecture/<run>>
Rules: <skill>/SKILL.md, section "Rules".

List: python -I "<skill>/scripts/findings.py" --run "<run folder>" list --status candidate

Open each one. Wrong when:
- duplicate: generated, vendored, a template meant to be copied, test data, or boilerplate;
- misplaced: shared helper meant for several folders, public path, place the framework imposes;
- useless folder: package or tool marker that must exist;
- junk: tracked on purpose (fixture, sample read by tests) or referenced (rg its name);
- crowded or deep: layout the framework or language imposes, or prefix groups that are not real groups;
- cycle: edge only through type-only imports, or one package by design;
- naming or tests: style the framework imposes per file kind (components, routes, e2e folder).
Anything else that makes it false counts: say what.

Verdicts, one call per group of ids sharing a reason, ids separated by spaces:
python -I "<skill>/scripts/findings.py" --run "<run folder>" confirm <ids> --why "<what you checked>"
python -I "<skill>/scripts/findings.py" --run "<run folder>" refute <ids> --why "<what disproves it>"
Rule 0 confirmations get --points 0.5 to 3.

Finish with this block and nothing after it:
VERIFIER REPORT
confirmed: <ids>
refuted: <ids>
doubts: <ids where the call was close, with the reason, or none>
`````
