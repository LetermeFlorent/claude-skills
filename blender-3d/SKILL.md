---
name: blender-3d
description: Use when working in Blender or on a .blend file, writing or running a bpy script, modeling, sculpting, UV unwrapping, texturing (realistic PBR or stylised), baking, shading, rigging, animating, rendering, using modifiers or geometry nodes, cleaning a mesh, or importing and exporting .glb, .gltf, .fbx, .obj or .stl for a game, or when a bpy call fails with "context is incorrect", "poll() failed", an unknown keyword or a missing attribute, or when a model must match a request or a reference image.
---

# Blender 3D

Blender renames operators, properties and nodes between versions, and memory mixes versions. Every action
(operator, modifier, node, property, export option) is checked in the Blender docs of the installed version
first. Not read = not done.

## Scripts: full control, no MCP

`<skill>/scripts`, Python standard library, run with `python -I`. They find Blender through `BLENDER_EXE`,
the PATH, `~/Tools/blender-*` or the usual install folders, run it headless at low priority, and print only
what matters. Exit 2 = refused (reason printed), exit 1 = Blender or the script failed (traceback printed).

| Script | Does |
|---|---|
| `run.py <file or -> <script.py> [--save new.blend]` | runs any bpy script on a `.blend`, on any file an importer reads (`.glb`, `.fbx`, `.obj`, `.usd`...), or on an empty scene (`-`); `--save` refuses the source path |
| `api.py <query>` | from the installed Blender: `bpy.ops.mesh.bevel` (parameters, types, defaults, enum values), `BevelModifier` or any `bpy.types` name, a node such as `ShaderNodeBsdfPrincipled` (its sockets), any Python path such as `bmesh.ops.extrude_face_region` or `mathutils.Vector` (signature, docs, members), or a word to search every operator and type |
| `shots.py <file> <out_dir> [--engine workbench/eevee/cycles] [--views ...] [--prefix 03-]` | renders captures framing every object, adds a light and world only when missing, never saves the file; views `front back left right side top bottom three_quarter` or `elevation:azimuth` |
| `docs.py search <words> [--docs api]` | searches the manual (or API) index of the installed version, prints the best page URLs |
| `docs.py page <url or path> [--find word]` | prints only the page's text, without menus; `--find` keeps the lines around a word |
| `live.py start [file.blend]`, `run <script.py>`, `shots <out_dir> [shots options]`, `status`, `stop` | visible mode: opens a Blender window the user watches, runs each script inside it (3D view context set), captures from a copy, closes it without saving |
| `info.py <file>` | version, objects, transforms and sizes, vertices, faces, triangles, non-manifold edges, loose parts, UV layers, materials, images (missing ones flagged), procedural textures to bake, modifiers, bones, actions |

Nothing is hard-coded to a Blender version: `run.py` runs any API, `docs.py` reads the docs of the
installed version, `api.py` reads names from the running
Blender, importers are found by their file filter, so features added in later versions work unchanged.
Add-ons and extensions the user installed load only with `BLENDER_KEEP_PREFS=1` (default is factory
settings, so results do not depend on the user's preferences).

## Hidden or visible

Hidden by default: every step runs headless with `run.py`, nothing appears on screen. When the user asks
to see Blender, switch at once, mid-task:

1. `live.py start <latest step .blend>` opens the window on the current state.
2. Every next step: `live.py run <script.py>`; captures: `live.py shots <work>/shots --prefix <step>-`.
   Scripts save their own step file: `bpy.ops.wm.save_as_mainfile(filepath=<new path>, copy=True)`.
   What the user sees: a step with `bpy.ops.screen.screenshot(filepath=<png>)`, then open the PNG.
   The window opens in Material Preview so the user sees materials and textures; never switch it to
   Solid, which shows every object grey.
3. Back to hidden when the user asks, or at the end: save the step file, then `live.py stop`. Leave the
   window open only when the user says so. The user closing the window ends visible mode: go on hidden
   from the last saved step.

## 1. Version first

`python -I <skill>/scripts/api.py` prints the version (or `blender --version`), then use `<x.y>` of that
version:

| Docs | URL |
|---|---|
| Manual: what a tool does, its options, its limits | `https://docs.blender.org/manual/en/<x.y>/` |
| Python API: exact names and parameters | `https://docs.blender.org/api/<x.y>/` |
| API changes of the version | `https://docs.blender.org/api/<x.y>/change_log.html` |
| API traps (context, modes, stale data) | `https://docs.blender.org/api/<x.y>/info_gotcha.html` |

Docs pages are read with `docs.py`, not a web fetch: a fetched page is mostly menus and gets cut before
its content.

## 2. Pick the tool from every option

Before choosing how to do a step, open the manual section that lists all tools of that domain
(`docs.py page <section>index.html`, or `docs.py search <step>`) and compare them, instead of using the
first tool remembered:

| Step | Manual section listing the options |
|---|---|
| Shape a mesh | `modeling/meshes/editing/`, `modeling/modifiers/` |
| Procedural shape, scatter, arrays | `modeling/geometry_nodes/` |
| Sculpt, paint | `sculpt_paint/` |
| UVs | `modeling/meshes/uv/` |
| Materials | `render/shader_nodes/` |
| Rig, animate | `animation/` |
| Render | `render/` |
| Import, export | `files/import_export/` |

Take the tool that does the step with the least destructive change (a modifier before an applied edit).
A creature or any organic body is one mesh, never primitives stuck together: an edge skeleton with the
Skin modifier (radii per vertex through `bm.verts.layers.skin.verify()`), Subdivision, then sculpt or
Displace for muscles and folds; thin parts like wing membranes are their own mesh along their bones.
Anything that moves gets its rig in the same work: a skeleton vertex at every joint (shoulder, elbow,
wrist, knee, each neck and tail segment, jaw, wing fingers) so loops sit where it bends; mark one root
(`bm.verts.ensure_lookup_table()` first: adding the skin layer frees the old vertex references), then
`bpy.ops.object.skin_armature_create(modifier=<skin>)` makes one bone per edge with weights; other meshes
get `parent_set(type="ARMATURE_AUTO")`. Every mesh is parented to the armature. Proof: pose neck, tail,
a leg and a wing, capture, check nothing tears or stays behind, then reset the pose.

## 3. Before every action, read its page

No operator, modifier, node or export runs before these four steps for it.

1. Manual page of the tool: `docs.py search <tool>`, then `docs.py page <url>`: behaviour, options, what
   it breaks.
2. API page for the script call: `docs.py page bpy.ops.<module>.html --docs api --find <name>`, same for
   `bpy.types.<Type>.html` and `bmesh.ops.html`.
3. Check the real names in the installed Blender, not from memory: `api.py bpy.ops.mesh.bevel`,
   `api.py BevelModifier`, `api.py ShaderNodeBsdfPrincipled`, or `api.py <word>` when the name is unknown.
4. Write the call with the names just read. Report names the pages read.

## 4. Running scripts

Every change is a bpy script run by `run.py`, one step per script, each step saved to a new file:
`run.py work/02.blend step3.py --save work/03.blend`. Blender runs with `--python-exit-code 1`: a Python
error fails the command with its traceback. Export is a step like any other, its options read first:
`run.py work/05.blend export.py` with `bpy.ops.export_scene.gltf(filepath=..., export_format="GLB")`.

- Never save over the user's `.blend`: `run.py` refuses it; scripts that save themselves use a new path.
- A `DeprecationWarning` in the output: replace the call now; the replacement is on the API page of that
  type (`docs.py page bpy.types.<Type>.html --docs api --find <name>`) or in `change_log.html`.
- Scripts prefer `bpy.data` and `bmesh` to `bpy.ops`: operators depend on the active object, mode and area.
  An operator that must run gets its context with `bpy.context.temp_override(...)` and the right mode.

## 5. Textures

The request sets the style; its words go on the checklist. No style word and no reference image: ask the
user realistic or stylised before texturing, never pick one silently.

| Request | Textures |
|---|---|
| Realistic, photo, real object | full PBR set: base colour, roughness, metallic, normal, ambient occlusion, height when the surface has relief; 2K to 4K; real-world scale on the UVs, even texel density; wear, dirt and variation where the real object has them; judged in Cycles under an HDRI |
| Stylised, cartoon, low poly, pixel, toon | flat colours, hand-painted or palette textures, small sizes (pixel art: nearest filtering, exact pixel grid); judged in Eevee or Workbench |

1. Read the manual pages of the method chosen: `sculpt_paint/texture_paint/`, `render/shader_nodes/`,
   `modeling/meshes/uv/`, and for baking `render/cycles/baking.html`.
2. Image textures need UVs first: unwrapped, no overlap where textures differ, seams where they hide.
   Flat colours from material values need none.
3. Model for a game or any export: bake procedural nodes, lighting and high-poly detail to image textures,
   plugged into Principled BSDF, before export: the glTF exporter keeps only those (its page:
   `addons/scene_gltf2.html`; it splits UDIM tiles into separate images, all on one UV map). Re-imported
   file captured to check the textures came through. Every part with a node material, small ones too (horns,
   claws, teeth, spikes), gets UVs and its own bake: a part without baked images exports as one flat colour.
4. Realistic means the real surface pattern, not a tint: scales, pores, plates, grain or weave built from
   Voronoi, Wave or painted masks whose cells and crevices drive colour, roughness and height together;
   colour that changes by zone (belly lighter than back, dark crevices, worn tips) from masks on object
   coordinates, a gradient or ambient occlusion; variation at two scales or more. Noise on a colour ramp
   alone is not a realistic texture. Each part gets the pattern its real material has, never one pattern
   copied everywhere: a wing membrane is thin skin with veins, folds and light through it, no scales; a horn
   is ringed keratin, dark base, pale worn tip. Relief strong enough to cast shade at `--zoom 4`: the baked
   normal map shows every cell clearly; a surface that looks painted on has its height too weak.
5. Captures of section 6 show the textures from a distance and close up (`shots.py --zoom 4`, one part: `--object Horn_L`), and every
   baked image is opened too: the pattern must be readable in both, a uniform tint fails the style item.

## 6. Look after every action

The work needs a model that sees images. An agent without image input stops before any change and tells
the user a model with vision is needed: numbers alone never say a model looks right.

1. Before the first change, write the request as a checklist of what can be seen: shape, proportions,
   parts, colours, style, pose, polygon budget. A reference image is opened and looked at first.
2. After every action that changes what is seen: `shots.py <file> <work>/shots --prefix <step>-`
   (front, side, top, three-quarter). Workbench for shape, `--engine eevee` or `cycles` for materials,
   extra `--views` (`back`, `45:120`) for parts hidden in the four.
3. Open every capture `shots.py` printed with the image-reading tool, all views, not one or two. Write
   what is seen, then compare it item by item with the checklist and the reference.
4. A gap: fix it, render again, look again. Stop only when every item matches, or the gap left is named
   to the user with its reason.

Never say it looks right, close or done without having opened the captures of that step: the closest
result to the request is the goal, not a model that only runs.

## 7. Traps

| Seen | Rule |
|---|---|
| `poll() failed, context is incorrect` | wrong mode, no active or selected object, or no area: set them or use `temp_override`, read the operator's page |
| Unknown keyword, missing attribute | name changed in this version: read `change_log.html`, check with step 3 |
| Export for a game engine | read the exporter page; apply scale and rotation, check axes, units and the engine's limits (triangles, bones, texture size) |
| Mesh for 3D printing or games | `info.py` before export: non-manifold edges are counted after welding vertices closer than 0.00001, so separate parts that touch show up there too |
| Baked or generated image shows `MISSING` in `info.py` | set `image.filepath_raw` and `image.file_format`, then `image.save()`, before the export or save |
| Edits in a loop | `bmesh` on the data, written back once, instead of an operator per element |

## 8. Proof

Done only after these ran this session:

1. The script exits 0 with `--python-exit-code 1`.
2. `info.py` on the result: objects, vertices, faces, materials, non-manifold edges, missing images.
3. Final captures from every view opened, each checklist item matched or its gap named.
4. Export: `info.py <exported file>` (it imports the file into an empty scene itself) shows the same objects,
   triangles, materials and images, and `shots.py` on it shows the textures came through.
5. Report: version, pages read, tools chosen and why, counts, file paths.
