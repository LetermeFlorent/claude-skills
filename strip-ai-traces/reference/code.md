# Code, tests and reviews

Match the files next to the one you edit. `clean-code` holds file size and naming rules; this page holds what gives a model away.

## What the scan finds in code

`by hand` row = chatbot residue or a placeholder. `flag` row = typography, emoji or an attribution on a code line: in a comment fix it, in a string literal it is a value (a pattern list stays), so propose the new string and ask. In page and style files it also reports the interface defaults of `visual.md`. Placeholders it knows: `// ... existing code ...`, `... rest of the code ...`, `TODO: implement`, an `Example usage` block, `your_api_key_here`, `replace with your`, `[insert ...]`.

## Habits to drop

Each shows in generated code far more than in human code.

- Comments restating the next line, section banners (`# ===== Helpers =====`), `# Step 1:`, `# Note:`, `# Helper function to`.
- Docstrings on trivial functions, `Args:` / `Returns:` blocks by default, one docstring shape on every function.
- Imports, parameters or config options nobody uses.
- Broad `try` / `except Exception` ending on a `print`; defensive checks on values the type or caller guarantees.
- `if __name__ == "__main__":` demo or sample output in a module that is not a script.
- Emoji or decorated console output, log lines in full sentences ending on "!".
- Version pins or API calls written from memory: check the version the project uses.
- Series of generic identifiers (`data`, `result`, `temp`, `item`, `helper`, `utils`, `manager`) when the domain has a word.

## Tests

Mock the boundary, never call a real API. Never assert a value you did not compute from the code. Keep the project's test naming. No test that only checks a mock was called.

## Review comments

No "consider extracting", "for better readability", reflex "nit:", or praise before the point. Name problem, line, fix; one comment per problem.

## Files an agent leaves behind

`IMPLEMENTATION_SUMMARY.md`, `CHANGES_SUMMARY.md`, `FIX_NOTES.md`, `REFACTORING_PLAN.md`, `SESSION_LOG.md`, `repro_*.py`, `scratch_*.js`, `debug_*.sh`: scan flags them by name. Delete the ones you created, ask about the others. Notes and reports go in `.ia/` or the temporary folder, never in the repository.
