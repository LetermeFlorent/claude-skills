# neoforge-modding

To install it, see `INSTALL.md` at the root of the repository.

Loads by itself when an agent works on a Minecraft Java mod built on NeoForge. It makes the agent:

1. read the project's build files to find the exact Minecraft, NeoForge, mappings and Java versions;
2. read the official docs page of that exact version before writing any code;
3. check every class and method name in the real game sources on disk;
4. follow the NeoForge rules that agents get wrong most often;
5. prove the work with a build and, when needed, a test server.

Only `SKILL.md` is needed.

## Not tested yet

Written from the official docs on 2026-11-20 without trial runs: no Java or mod project was on this PC.
The first real uses may show mistakes the skill does not catch yet.
