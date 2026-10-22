# Verifier brief

Sent as the prompt of one fresh agent once every candidate is in findings.json. The verifier never
saw the measuring, so it has no stake in the candidates. It is told to refute, and it confirms only
what survives. Fill every `<...>` and send the block as is.

`````text
You verify the candidates of a clean-code audit. The audit is read-only: you edit no project file
and run no command that writes, apart from findings.py below.

Project root: <absolute project root>
Run folder: <absolute path of .ia/clean-code/<run>>
Rules: <absolute path of the skill>/SKILL.md, section "The rules". Read it first.

List the candidates:
python -I "<skill>/scripts/findings.py" --run "<run folder>" list --status candidate

For each one, open the file at the line and try to prove it wrong. It is wrong when:
- the line is test data, a fixture, a snapshot or a translation file;
- the comment is a tool directive, a licence header, or the doc of a public API;
- a file "never imported" is an entry point: a route file, a config the framework loads by name,
  a bin or script in the manifest, a dynamic import, a worker, a CLI;
- an unused import is there for its side effect (polyfill, CSS, registration);
- every hardcoded value listed is already named once, is 0, 1, -1, an empty string or a boolean,
  or is a keyword a library defines for its own arguments (`action="store_true"`). A protocol number, a method name or a unit written in place is still rule 18: it gets
  one name (reference/values.md). When only some values of a finding hold, the finding stands;
- a French-looking identifier is English, a proper noun, or a key fixed by an outside contract;
- a folder over the file limit follows the framework's own layout;
- a secret is a placeholder, a public key, or a sample value in a file marked as an example.
Anything else that makes the candidate false counts too: say what.

Open every id on its own. Then write the verdict, one call per group of ids sharing the same
reason:
python -I "<skill>/scripts/findings.py" --run "<run folder>" confirm <ids> --why "<what you checked>"
python -I "<skill>/scripts/findings.py" --run "<run folder>" refute <ids> --why "<what disproves it>"

Caps lower the note on their own, so check them hardest. Keep a cap only when it holds:
- secret: a live value in a tracked file, not a sample;
- swallowed: the error is lost on a path that matters (payment, save, auth, data write);
- test-in-prod: the test or seed code really reaches the production build;
- attribution: the trailer or the workflow is really there;
- build: the build or typecheck command really fails, with its output.
When it does not hold, confirm with --cap none: a cap that fails never refutes the defect under
it, and a swallowed error on a path without stakes is still rule 8. Rule 0 findings get --points
from 0.5 to 3.

Finish with this block and nothing after it:
VERIFIER REPORT
confirmed: <count>
refuted: <count>
caps kept: <ids and cap names, or none>
doubts: <ids where the call was close, with the reason, or none>
`````
