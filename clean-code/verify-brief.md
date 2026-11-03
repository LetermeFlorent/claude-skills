# Verifier brief

Prompt of one fresh agent once every candidate is in findings.json. Fill every `<...>` and send the
block as is.

`````text
You verify the candidates of a clean-code audit. Read-only: edit no project file and run nothing
that writes, apart from findings.py below. You are told to refute: confirm only what survives.

Project root: <absolute project root>
Run folder: <absolute path of .ia/clean-code/<run>>
Rules: <skill>/SKILL.md, section "The rules". Read it first.

List: python -I "<skill>/scripts/findings.py" --run "<run folder>" list --status candidate

Open each one at its line. A candidate is wrong when:
- the line is test data, a fixture, a snapshot or a translation file;
- the comment is a tool directive, a licence header or public API doc;
- a "never imported" file is an entry point (route, framework-loaded config, manifest bin or
  script, dynamic import, worker, CLI);
- an unused import is there for its side effect;
- every hardcoded value is a case of "Not a finding" in reference/values.md or a library keyword
  (`action="store_true"`); when only some hold, the finding stands;
- a French-looking identifier is English, a proper noun, or a key fixed by an outside contract;
- a folder over the file limit follows the framework layout;
- a secret is a placeholder, public key, or sample value in a file marked as example.
Anything else that makes it false counts: say what.

Verdicts, one call per group of ids sharing a reason:
python -I "<skill>/scripts/findings.py" --run "<run folder>" confirm <ids> --why "<what you checked>"
python -I "<skill>/scripts/findings.py" --run "<run folder>" refute <ids> --why "<what disproves it>"

Check caps hardest and keep one only when it holds: secret (live value in a tracked file),
swallowed (error lost on a path that matters: payment, save, auth, data write), test-in-prod (test
or seed code reaches the production build), attribution (trailer or workflow really there), build
(command really fails, with output). Otherwise confirm with --cap none: a failed cap never refutes
the defect under it. Rule 0 confirmations get --points 0.5 to 3.

Finish with this block and nothing after it:
VERIFIER REPORT
caps kept: <ids and cap names, or none>
doubts: <ids where the call was close, with the reason, or none>
`````
