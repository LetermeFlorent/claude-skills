---
name: blender-3d
description: Use when working in Blender or on a .blend file, writing or running a bpy script, modeling, sculpting, UV unwrapping, texturing (realistic PBR or stylised), baking, shading, rigging, animating, rendering, using modifiers or geometry nodes, cleaning a mesh, or importing and exporting .glb, .gltf, .fbx, .obj or .stl for a game, or when a bpy call fails with "context is incorrect", "poll() failed", an unknown keyword or a missing attribute, or when a model must match a request or a reference image.
---

# Blender 3D

Blender renames operators, properties and nodes between versions, and memory mixes versions. Every action
(operator, modifier, node, property, export option) is checked in the Blender docs of the installed version
first. Not read = not done.

## 1. Version first

`blender --version` (or `bpy.app.version_string` inside Blender), then use `<x.y>` of that version:

| Docs | URL |
|---|---|
| Manual: what a tool does, its options, its limits | `https://docs.blender.org/manual/en/<x.y>/` |
| Python API: exact names and parameters | `https://docs.blender.org/api/<x.y>/` |
| API changes of the version | `https://docs.blender.org/api/<x.y>/change_log.html` |
| API traps (context, modes, stale data) | `https://docs.blender.org/api/<x.y>/info_gotcha.html` |

## 2. Pick the tool from every option

Before choosing how to do a step, open the manual section that lists all tools of that domain and compare
them, instead of using the first tool remembered:

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

## 3. Before every action, read its page

No operator, modifier, node or export runs before these four steps for it.

1. Manual page of the tool: behaviour, options, what it breaks.
2. API page for the script call: `bpy.ops.<module>.html`, `bpy.types.<Type>.html`, `bmesh.html`.
3. Check the real names in the installed Blender, not from memory:
   `blender --background --python-expr "import bpy; print([p.identifier for p in bpy.ops.mesh.bevel.get_rna_type().properties])"`.
4. Write the call with the names just read. Report names the pages read.

## 4. Running scripts

Every script runs headless, from a copy of the file.

- `blender --background <file.blend> --python <script.py> --python-exit-code 1`: a Python error fails the
  command instead of being lost in the log.
- Never save over the user's `.blend`: `bpy.ops.wm.save_as_mainfile(filepath=<new path>)`, or a copy first.
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
2. UVs first: unwrapped, no overlap where textures differ, seams where they hide.
3. Model for a game or any export: bake procedural nodes, lighting and high-poly detail to image textures,
   plugged into Principled BSDF, no UDIM, before export: the glTF exporter keeps only those (its page:
   `addons/scene_gltf2.html`). Re-imported file captured to check the textures came through.
4. Captures of section 6 show the textures close up and from a distance; the checklist item for the style
   is compared like the others.

## 6. Look after every action

The work needs a model that sees images. An agent without image input stops before any change and tells
the user a model with vision is needed: numbers alone never say a model looks right.

1. Before the first change, write the request as a checklist of what can be seen: shape, proportions,
   parts, colours, style, pose, polygon budget. A reference image is opened and looked at first.
2. After every action that changes what is seen, render captures from front, side, top and three-quarter,
   camera aimed at the centre of all objects and far enough to frame them: Workbench for shape, Eevee or
   Cycles for materials. `scene.render.filepath` then `bpy.ops.render.render(write_still=True)`, files in
   `<work folder>/shots/<step>-<view>.png`.
3. Open every capture with the image-reading tool and look at it. Write what is seen, then compare it item
   by item with the checklist and the reference.
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
| Mesh for 3D printing or games | check non-manifold edges, flipped normals, loose parts with `bmesh` before export |
| Edits in a loop | `bmesh` on the data, written back once, instead of an operator per element |

## 8. Proof

Done only after these ran this session:

1. The script exits 0 with `--python-exit-code 1`.
2. Counts printed from the result: objects, vertices, faces, materials, non-manifold edges.
3. Final captures from every view opened, each checklist item matched or its gap named.
4. Export: the file imported again into an empty scene with the same counts.
5. Report: version, pages read, tools chosen and why, counts, file paths.
