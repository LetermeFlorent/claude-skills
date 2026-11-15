# Final optimisation

Last work box of drive-project. Goal: run uses least resource possible (CPU, memory, disk, network,
energy), nothing degraded. Paths: only the `files:` of your box. Defects elsewhere reported, not fixed.

Rules:
1. Read and understand first: code, docs and installed versions of what you touch. Never optimise from
   memory or guess.
2. Measure before and after with the project's own tools or a profiler, same input, same machine. Paste
   both. No measurable gain, or any loss in behaviour, output, security, readability, accessibility or
   tests: restore that change.
3. Reuse what exists (helper, library, platform feature) before writing new code.
4. Use the technologies named in the start answers; avoid those named to avoid. Answer `none given`: pick
   the project's own stack, add no dependency for a few lines.
5. Graphics card only when start answer allows it and the measure shows gain over CPU, with a CPU
   fallback when no card is present. Answer `never`: not used.
6. Cheapest correct structure and type, no allocation in a hot loop, lazy work, cache only what is
   measured, remove unused work, load and build only what production needs.
7. Whole check of the box's plan line passes: tests, typecheck, lint, build. Same behaviour proven, not
   assumed.
8. Code rules of clean-code (`<repo>/clean-code/SKILL.md`, Writing code) bind every line written.

Report: per change one line, `before -> after` with unit; changes restored and why; `skipped:` what was
not checked.
