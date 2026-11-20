---
name: neoforge-modding
description: Use when writing, fixing or porting a Minecraft Java mod on NeoForge, when a project has neoforge.mods.toml, net.neoforged imports, ModDevGradle or NeoGradle, DeferredRegister, a mod event bus, payload networking, a Mixin or data generation, or when a NeoForge build fails with "cannot find symbol", "package net.minecraftforge does not exist", an unknown event or a client class loaded on a dedicated server.
---

# NeoForge modding

Minecraft and NeoForge change names and APIs every version, and memory mixes NeoForge with old Forge.
Every class, method, event and registry call in the code comes from a page read or a source line seen
this session, for the project's exact versions. Not read = not written.

## 1. Versions first

Before any code, read `gradle.properties`, `build.gradle(.kts)`, `settings.gradle` and the metadata file,
then write down:

| Value | Where |
|---|---|
| Minecraft, NeoForge | `gradle.properties` (`minecraft_version`, `neo_version`) |
| Plugin | `net.neoforged.moddev` = ModDevGradle, `net.neoforged.gradle.userdev` = NeoGradle |
| Mappings | Mojang names; Parchment if `parchment` is set |
| Java | `java.toolchain` |
| Metadata | `src/main/resources/META-INF/neoforge.mods.toml` (older ports: `mods.toml`; keep what the version uses) |

## 2. Docs before code

Open the docs of that exact Minecraft version and read the page of the feature before writing it:

- `https://docs.neoforged.net/docs/<version>/` (current version: `https://docs.neoforged.net/docs/`), version
  selector at the top. Read the page of the topic: registries, events, networking (payloads), data
  generation, capabilities or data attachments, mod files.
- Porting between versions: primers at `https://docs.neoforged.net/primer/docs/`, the one for each
  version crossed, read before touching code.
- Toolchain (run tasks, plugin settings): `https://docs.neoforged.net/toolchain/docs/`.

Report names the URLs read. A page not found for that version: say so, then rely on sources only.

## 3. Real names from the sources

Docs give the idea, sources give the exact signature.

1. `./gradlew tasks --all` gives the real task names (`runClient`, `runServer`, data runs). Never guess.
2. Find the sources jar: ModDevGradle `minecraft-patched-<version>-merged` sources, NeoGradle
   `neoforge-<version>` sources: `find ~/.gradle/caches build .gradle -name "*sources*.jar"`.
3. Read the class: `unzip -p <jar> net/neoforged/<path>/<Class>.java | grep -n "<method>"`, same for
   `net/minecraft/...`.
4. Copy the signature from what you read: package, name, parameter types, return type.

## 4. Traps

| Seen in the project | Rule |
|---|---|
| Any import | `net.neoforged.*`, never `net.minecraftforge.*`; a Forge tutorial is not a source |
| Mod constructor | takes `IEventBus modEventBus` (and `ModContainer` when needed); registration and lifecycle listeners go on that bus |
| Game events (ticks, players, levels) | `NeoForge.EVENT_BUS`; check in the event's source which bus it is posted on |
| `@EventBusSubscriber` | bus value and `Dist` read from that version's annotation source |
| Registration | `DeferredRegister` registered on the mod bus in the constructor; never `Registry.register` at runtime |
| Networking | payloads registered in the payload registration event of that version; handler side and thread read from docs |
| Client code | rendering, screens, keybinds only in classes loaded from `Dist.CLIENT` subscribers or client entry; common code never imports `net.minecraft.client` |
| A Mixin | config listed in `neoforge.mods.toml` `[[mixins]]`; client targets in its `client` list; `@Inject`/`@WrapOperation` before `@Overwrite` |
| Data generation | providers on the data-gen event of that version; run the data task, keep generated files where the project keeps them |
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
