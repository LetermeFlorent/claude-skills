# blender-3d

To install it, see `INSTALL.md` at the root of the repository.

Loads by itself when an agent works with Blender: a `.blend` file, a Python script for Blender, a model to
make, clean, texture, rig or export for a game. It makes the agent:

1. find the installed Blender version and use the manual and Python docs of that exact version;
2. look at every tool Blender offers for the step before choosing one;
3. read the docs page of each tool before using it, and check its real names in the installed Blender;
4. make textures realistic or stylised as the request says (it asks when the request does not say),
   and turn them into images before any export for a game so they are not lost;
5. after every change, render pictures from several angles, look at them and compare them with what
   you asked, fixing until it matches (it needs a model that can see images);
6. run scripts so that errors are not missed, and never overwrite your `.blend`;
7. prove the result with counts, final pictures and a re-import of exported files.

It drives Blender through small Python scripts in `scripts/`, no MCP server: run any Blender script,
read operator and node names from the installed Blender, search and read the docs of that version, render
captures, list what a file holds. Nothing in them is tied to one Blender version, so features added later
work without changing the scripts.

Blender stays hidden by default. Ask to see it at any time and it opens a Blender window where each step
shows live; ask again and it closes it and goes on hidden.

Needs Blender installed (or `BLENDER_EXE` pointing at it) and Python 3. Add-ons you installed in Blender are
used only when `BLENDER_KEEP_PREFS=1` is set.

## What was tested

On Windows 11 with Blender 5.3.0, 2026-11-20:

- every script run for real: scripts on an empty scene, a `.blend` and a `.glb`; captures with Workbench,
  Eevee and Cycles; glTF export and re-import; docs search and page reading; the visible window opened,
  driven, captured and closed;
- refusals and failures: missing files, saving over the source, unknown engine or format, Python errors;
- unit tests: `python -I tests/test_pure.py`;
- agents given the same model tasks with and without the skill (Sonnet and Haiku): without it they read no
  docs and looked at one picture; with it they read the docs pages, checked names, opened every view and
  fixed what the captures and counts showed.

Not tested on Linux or macOS.
