---
name: forge-modding
description: Use when writing, fixing or porting a Minecraft Java mod on Minecraft Forge, when a project has META-INF/mods.toml with net.minecraftforge imports, ForgeGradle, DeferredRegister, @SubscribeEvent, SimpleChannel or a Mixin, or when a Forge build fails with "package net.minecraftforge.eventbus.api does not exist", "cannot find symbol" on IEventBus or EVENT_BUS, an event that no longer fires, or a client class loaded on a dedicated server.
---

# Forge modding

Minecraft and Forge change names and APIs every version, Forge 1.21.6 rewrote its event bus, and memory
mixes Forge with NeoForge. Every class, method, event and registry call in the code comes from a page read
or a source line seen this session, for the project's exact versions. Not read = not written.

## 1. Versions first

Before any code, read `gradle.properties`, `build.gradle`, `settings.gradle`,
`src/main/resources/META-INF/mods.toml`, then write down:

| Value | Where |
|---|---|
| Minecraft, Forge | `gradle.properties` (`minecraft_version`, `forge_version`) or the `minecraft` dependency line |
| Mappings | `mappings channel:` in `build.gradle`: `official` (Mojang names) or `parchment` |
| Java | `java.toolchain` |
| Event bus | Forge 56 (Minecraft 1.21.6) or later = EventBus 7; older = `IEventBus` |

## 2. Survey at project start

First session on a project, or versions changed since the last survey: before the task, learn what this
version offers, so the code uses the right tool instead of the one remembered.

1. Read the whole table of contents of the docs for that version (every section, not only the task's),
   and open each page whose title is new to you.
2. Read the Forge changelog of the version in use, the EventBus 7 guide on Forge 56 or later, and the
   Minecraft release notes of that version.
3. Note what changed from the previous Minecraft version: renamed classes, removed systems, new ones
   (data components, new registries, new events).
4. Write `.ia/minecraft-docs.md` in the project: versions on the first line, then one line per feature
   with its URL. Next session: same versions = read that file instead of surveying again.

The survey is never skipped because the task looks small: a small task on an unknown version is where
remembered APIs break.

## 3. Docs before code

Open the docs of that exact version and read the page of the feature before writing it:

- `https://docs.minecraftforge.net/en/latest/`, version selector at the top; pick the project's version.
  Read the page of the topic: registries, events, networking (SimpleImpl), data generation, mod files.
- The docs stop before EventBus 7. Forge 56 or later: read the EventBus 7 migration guide
  `https://gist.github.com/PaintNinja/ad82c224aecee25efac1ea3e2cf19b91` and the changelog of the Forge
  version in use, `https://maven.minecraftforge.net/net/minecraftforge/forge/<mc>-<forge>/forge-<mc>-<forge>-changelog.txt`.
- Porting: read the changelog entries between the two Forge versions before touching code.

Report names the URLs read. A page not found for that version: say so, then rely on sources only.

## 4. Real names from the sources

Docs give the idea, sources give the exact signature.

1. `./gradlew tasks --all` gives the real task names (`runClient`, `runServer`, `runData`). Never guess.
2. Find the sources jar: `find ~/.gradle/caches build .gradle -name "*sources*.jar"` (the Forge and
   Minecraft jar of the versions in use, plus `eventbus` on Forge 56 or later).
3. Read the class: `unzip -p <jar> net/minecraftforge/<path>/<Class>.java | grep -n "<method>"`, same
   for `net/minecraft/...`.
4. Copy the signature from what you read: package, name, parameter types, return type.

## 5. Traps

| Seen in the project | Rule |
|---|---|
| Any import | `net.minecraftforge.*`, never `net.neoforged.*`; a NeoForge tutorial is not a source |
| Forge 56 or later | `BusGroup` and per-event `BUS`; `SubscribeEvent` is in `net.minecraftforge.eventbus.api.listener`; cancel = listener returns `true`; check `register` and `addListener` signatures in the `eventbus` sources |
| Forge before 56 | `IEventBus`, `MinecraftForge.EVENT_BUS`, `FMLJavaModLoadingContext` mod bus, `setCanceled` |
| Registration | `DeferredRegister` registered on the mod bus (or mod `BusGroup`) in the constructor |
| Networking | the channel API of that version (`SimpleChannel` or `ChannelBuilder`), read from sources |
| Client code | rendering, screens, keybinds only in classes loaded for `Dist.CLIENT`; common code never imports `net.minecraft.client` |
| A Mixin | config declared the way that Forge version reads it (`MixinConfigs` manifest or `mods.toml`), checked in docs; client targets in its `client` list; `@Inject`/`@WrapOperation` before `@Overwrite` |
| Data generation | `GatherDataEvent` providers; run `runData`, keep generated files where the project keeps them |
| Hot path (`tick`, render) | no allocation, lookup or registry query per tick that can be cached once |

## 6. Proof

Done only after these ran this session:

1. `./gradlew build` ends in `BUILD SUCCESSFUL`. Failure: read the first javac error, check the name in
   the sources (step 4), fix, rebuild. Never claim it compiles without the run.
2. Change touches gameplay, registration, networking or a Mixin: `./gradlew runServer` until the log shows
   `Done (`, then stop it. A crash naming a client class = side leak. `runClient` when the change is visual.
   Server stops on the EULA: the user accepts the Minecraft EULA for test servers, so set `eula=true` in the
   run folder's `eula.txt` and start again.
3. Report: versions found, URLs read, signatures checked, build line.
