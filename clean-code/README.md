# clean-code

A skill and a command for Claude Code. To install it, see `INSTALL.md` at the root of the repository.

## Usage

`/clean-code` followed by a folder, an app or a file. With no argument, Claude asks for the scope. The skill also starts on a request to audit or tidy up, or when a file or folder has grown too big.

The audit touches nothing before you answer. A script measures what can be counted (file and folder sizes, dead code, comments, French names, hardcoded values, text outside translation files, images, AI traces, secrets), Claude reads the rest, and a fresh agent confirms or rejects each finding. The score out of 20 comes from a script, with caps: secret 5, broken build 8, swallowed error, shipped test code or AI signature 10.

Below 20, Claude writes a step-by-step plan, has it checked, then asks you: the whole plan, the safe steps only, or nothing. Each step is committed by `clean-commits`, never on failing tests, never pushed.

## Writing rules

For any code the skill writes: no comments, English names, no avoidable hardcoded value, text in translation files, files under 150 lines, images in WebP at 1x and 2x.

## Files

Each run goes into `.ia/clean-code/` at the project root (excluded from git). Thresholds can be set in `.ia/clean-code/config.json`. `SKILL.md` holds the procedure, `reference/` the detailed rules, `scripts/` the measurements, `tests/` the tests of the pure parts.
