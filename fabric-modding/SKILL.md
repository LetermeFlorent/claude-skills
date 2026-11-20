---
name: fabric-modding
description: Use when writing, fixing or porting a Minecraft Java mod on Fabric, when a project has fabric.mod.json, fabric-loom in build.gradle, Yarn or intermediary mappings, a Mixin, an entrypoint, Fabric API networking or data generation, or when a Fabric build fails with "cannot find symbol", a mapping error, a mixin apply failure or a client class loaded on a dedicated server.
---

# Fabric modding

Minecraft and Fabric change names and APIs every version, and memory mixes versions. Every class, method,
field, registry call and event in the code comes from a page read or a source line seen this session,
for the project's exact versions. Not read = not written.

## 1. Versions first

Before any code, read `gradle.properties`, `build.gradle(.kts)`, `settings.gradle`,
`src/main/resources/fabric.mod.json`, then write down:

| Value | Where |
|---|---|
| Minecraft, loader, Fabric API, Loom | `gradle.properties` (`minecraft_version`, `loader_version`, `fabric_version`), `plugins` block |
| Mappings | `mappings` line in `build.gradle`: `yarn`, `loom.officialMojangMappings()`, Parchment layer, or none |
| Java | `java.toolchain` or `sourceCompatibility` |
| Source sets | `loom { splitEnvironmentSourceSets() }` = client code in `src/client` |

## 2. Docs before code

Before writing, search the docs of that exact Minecraft version for the task's topic and read only the matching
pages, never the whole docs:

- `https://docs.fabricmc.net/<version>/develop/` (current version: `https://docs.fabricmc.net/develop/`).
  Pages: entrypoints and `fabric.mod.json` (`/develop/loader/fabric-mod-json`), networking
  (`/develop/networking`), data generation (`/develop/data-generation/setup`), Loom tasks (`/develop/loom/tasks`).
- Porting between versions: `/develop/porting/` of the target version, read whole before touching code.
- Fabric API Javadoc of the `fabric_version` in use for module and method names.

Report names the URLs read. A page not found for that version: say so, then rely on sources only.

## 3. Real names from the sources

Docs give the idea, sources give the exact signature.

1. `./gradlew tasks --all` gives the real task names of this Loom (`genSources`, `runClient`,
   `runServer`, `runDatagen` when data generation is set up). Never guess a task.
2. `./gradlew genSources`, then find the jar: `find ~/.gradle/caches .gradle -name "*minecraft*sources*.jar"`.
3. Read the class: `unzip -p <jar> net/minecraft/<path>/<Class>.java | grep -n "<method>"`. Same for
   `fabric-api` jars of the `fabric_version` in use.
4. Copy the signature from what you read: package, name, parameter types, return type.

## 4. Traps

| Seen in the project | Rule |
|---|---|
| `yarn` mappings | Yarn names (`MinecraftClient`, `Identifier`), never Mojang names (`Minecraft`, `ResourceLocation`) |
| Mojang mappings, or Minecraft 26.x | Mojang names; 26.x is unobfuscated, no Yarn, no refmap. Yarn to Mojang: Loom `migrateMappings`, then fix Mixins by hand |
| `splitEnvironmentSourceSets()` | `net.minecraft.client.*`, rendering, screens, keybinds only in `src/client`; `main` never imports them |
| No split source sets | client classes only behind `ClientModInitializer` and classes it alone loads |
| A Mixin | its JSON listed in `fabric.mod.json` `mixins`; client targets in its `client` array; `@Inject`/`@WrapOperation` before `@Overwrite`; target signature read from sources |
| Fabric API call | module present in `depends` and build; method checked in that version's jar |
| Data generator | entrypoint `fabric-datagen` in `fabric.mod.json`; run `runDatagen`, keep generated files where the project keeps them |
| Hot path (`tick`, render) | no allocation, lookup or registry query per tick that can be cached once |

## 5. Proof

Done only after these ran this session:

1. `./gradlew build` ends in `BUILD SUCCESSFUL`. Failure: read the first javac error, check the name in
   the sources (step 3), fix, rebuild. Never claim it compiles without the run.
2. Change touches gameplay, registration, networking or a Mixin: `./gradlew runServer` until the log shows
   `Done (`, then stop it. A crash naming a client class = side leak. `runClient` when the change is visual.
   Server stops on the EULA: the user accepts the Minecraft EULA for test servers, so set `eula=true` in the
   run folder's `eula.txt` and start again.
3. Report: versions found, URLs read, signatures checked, build line.
