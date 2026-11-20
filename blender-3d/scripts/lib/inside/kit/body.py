import bpy
from mathutils import Vector

from .parts import smooth


def body(name, chains, head):
    points, radii, edges, sizes = [], [], set(), {}
    for chain, joints in chains.items():
        indices = []
        for location, radius in joints:
            location = Vector(location)
            found = next((i for i, p in enumerate(points) if (p - location).length < 1e-4), None)
            if found is None:
                points.append(location)
                radii.append(radius)
                found = len(points) - 1
            indices.append(found)
        edges.update(tuple(sorted(pair)) for pair in zip(indices, indices[1:]) if pair[0] != pair[1])
        length = sum((points[b] - points[a]).length for a, b in zip(indices, indices[1:]))
        own = joints[1:] if len(joints) > 2 else joints
        sizes[chain] = (length, 2 * max(r if isinstance(r, (int, float)) else max(r) for _, r in own))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([p.to_tuple() for p in points], sorted(edges), [])
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.modifiers.new("Skin", "SKIN")
    for vertex, radius in zip(mesh.skin_vertices[0].data, radii):
        vertex.radius = radius if isinstance(radius, tuple) else (radius, radius)
    mesh.skin_vertices[0].data[0].use_root = True
    smooth(obj, 2)
    unit = sizes[head][0] or 1.0
    for chain, (length, width) in sizes.items():
        print(f"chain {chain}: length {length / unit:.2f} heads, widest {width / unit:.2f} heads")
    return obj


def rig(body_obj, others=()):
    bpy.context.view_layer.update()
    for obj in bpy.context.view_layer.objects:
        obj.select_set(obj == body_obj)
    bpy.context.view_layer.objects.active = body_obj
    skin = next(m for m in body_obj.modifiers if m.type == "SKIN")
    bpy.ops.object.skin_armature_create(modifier=skin.name)
    armature = next(m.object for m in body_obj.modifiers if m.type == "ARMATURE")
    for obj in others:
        for other in bpy.context.view_layer.objects:
            other.select_set(other in (obj, armature))
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    for obj in bpy.context.view_layer.objects:
        obj.select_set(False)
    body_obj.parent = armature
    body_obj.matrix_parent_inverse = armature.matrix_world.inverted()
    return armature
