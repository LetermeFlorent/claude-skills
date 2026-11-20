import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bmesh
import bpy
from util import args, load, say

WELD = 1e-5


def fmt(values):
    return "(" + ", ".join(f"{v:.3g}" for v in values) + ")"


def parts(bm):
    seen, count = set(), 0
    for start in bm.verts:
        if start.index in seen:
            continue
        count += 1
        stack = [start]
        seen.add(start.index)
        while stack:
            for edge in stack.pop().link_edges:
                for vert in edge.verts:
                    if vert.index not in seen:
                        seen.add(vert.index)
                        stack.append(vert)
    return count


def mesh_line(ob, deps):
    evaluated = ob.evaluated_get(deps)
    mesh = evaluated.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    verts, faces = len(bm.verts), len(bm.faces)
    tris = sum(len(face.verts) - 2 for face in bm.faces)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=WELD)
    bm.verts.index_update()
    open_edges = sum(1 for edge in bm.edges if not edge.is_manifold)
    line = (f"  mesh verts {verts} faces {faces} tris {tris} non-manifold edges {open_edges}"
            f" parts {parts(bm)} uv layers {len(mesh.uv_layers)}")
    bm.free()
    evaluated.to_mesh_clear()
    return line


def object_lines(ob, deps):
    yield (f"object {ob.name} type {ob.type} parent {ob.parent.name if ob.parent else '-'} location {fmt(ob.location)}"
           f" rotation {fmt(ob.rotation_euler)} scale {fmt(ob.scale)} size {fmt(ob.dimensions)}")
    if ob.type == "MESH":
        yield mesh_line(ob, deps)
    if ob.material_slots:
        names = (slot.material.name if slot.material else "<empty slot>" for slot in ob.material_slots)
        yield "  materials " + ", ".join(names)
    if ob.modifiers:
        yield "  modifiers " + ", ".join(f"{m.name}:{m.type}" for m in ob.modifiers)
    if ob.type == "ARMATURE":
        yield f"  bones {len(ob.data.bones)}"


def image_state(image):
    if image.packed_file or image.source == "GENERATED":
        return "packed" if image.packed_file else "generated"
    path = bpy.path.abspath(image.filepath)
    return path if os.path.exists(path) else f"MISSING {path}"


def material_lines(material):
    nodes = material.node_tree.nodes if material.node_tree else []
    images = [n for n in nodes if n.type == "TEX_IMAGE"]
    procedural = sorted({n.type for n in nodes if n.type.startswith("TEX_") and n.type != "TEX_IMAGE"})
    yield f"material {material.name} users {material.users} nodes {len(nodes)}"
    for node in images:
        state = image_state(node.image) if node.image else "no image"
        size = tuple(node.image.size) if node.image else ()
        yield f"  image {node.name} {node.image.name if node.image else '-'} {size} {state}"
    if procedural:
        yield "  procedural " + ", ".join(procedural) + " (bake to images before export)"


def main():
    source = args()[0]
    load(source)
    scene = bpy.context.scene
    deps = bpy.context.evaluated_depsgraph_get()
    say(f"blender {bpy.app.version_string} file {source}")
    say(f"scene {scene.name} engine {scene.render.engine} frames {scene.frame_start}-{scene.frame_end}"
        f" unit {scene.unit_settings.system} scale {scene.unit_settings.scale_length:g}")
    for ob in sorted(bpy.data.objects, key=lambda o: o.name):
        for line in object_lines(ob, deps):
            say(line)
    for material in bpy.data.materials:
        for line in material_lines(material):
            say(line)
    for action in bpy.data.actions:
        say(f"action {action.name} frames {fmt(action.frame_range)}")
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    say(f"total objects {len(bpy.data.objects)} meshes {len(meshes)} materials {len(bpy.data.materials)}"
        f" images {len(bpy.data.images)} actions {len(bpy.data.actions)}")


main()
