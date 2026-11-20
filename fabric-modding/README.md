# fabric-modding

To install it, see `INSTALL.md` at the root of the repository.

Loads by itself when an agent works on a Minecraft Java mod built on Fabric. It makes the agent:

1. read the project's build files to find the exact Minecraft, Fabric, mappings and Java versions;
2. on a new project, go through the whole docs of that version and its release notes, and keep a
   short list of every feature in `.ia/minecraft-docs.md`;
3. read the official docs page of that exact version before writing any code;
4. check every class and method name in the real game sources on disk;
5. follow the Fabric rules that agents get wrong most often;
6. prove the work with a build and, when needed, a test server.

Only `SKILL.md` is needed.

## Not tested yet

Written from the official docs on 2026-11-20 without trial runs: no Java or mod project was on this PC.
The first real uses may show mistakes the skill does not catch yet.
