---
name: blender-3d
description: Use when working in Blender or on a .blend file, writing or running a bpy script, modeling, sculpting, UV unwrapping, texturing, shading, rigging, animating, rendering, using modifiers or geometry nodes, cleaning a mesh, or importing and exporting .glb, .gltf, .fbx, .obj or .stl for a game, or when a bpy call fails with "context is incorrect", "poll() failed", an unknown keyword or a missing attribute.
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

## 5. Traps

| Seen | Rule |
|---|---|
| `poll() failed, context is incorrect` | wrong mode, no active or selected object, or no area: set them or use `temp_override`, read the operator's page |
| Unknown keyword, missing attribute | name changed in this version: read `change_log.html`, check with step 3 |
| Export for a game engine | read the exporter page; apply scale and rotation, check axes, units and the engine's limits (triangles, bones, texture size) |
| Mesh for 3D printing or games | check non-manifold edges, flipped normals, loose parts with `bmesh` before export |
| Edits in a loop | `bmesh` on the data, written back once, instead of an operator per element |

## 6. Proof

Done only after these ran this session:

1. The script exits 0 with `--python-exit-code 1`.
2. Counts printed from the result: objects, vertices, faces, materials, non-manifold edges.
3. A preview image rendered (Workbench or Eevee) and looked at.
4. Export: the file imported again into an empty scene with the same counts.
5. Report: version, pages read, tools chosen and why, counts, file paths.
