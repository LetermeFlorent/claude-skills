# blender-3d

To install it, see `INSTALL.md` at the root of the repository.

Loads by itself when an agent works with Blender: a `.blend` file, a Python script for Blender, a model to
make, clean, texture, rig or export for a game. It makes the agent:

1. find the installed Blender version and use the manual and Python docs of that exact version;
2. look at every tool Blender offers for the step before choosing one;
3. read the docs page of each tool before using it, and check its real names in the installed Blender;
4. run scripts so that errors are not missed, and never overwrite your `.blend`;
5. prove the result with counts, a preview image and a re-import of exported files.

Only `SKILL.md` is needed.

## Not tested yet

Written from the Blender docs on 2026-11-20 without trial runs. The first real uses may show mistakes the
skill does not catch yet.
