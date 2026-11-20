import math
import random

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def give(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj


def smooth(obj, levels=2):
    sub = next((m for m in obj.modifiers if m.type == "SUBSURF"), None) or obj.modifiers.new("Subdivision", "SUBSURF")
    sub.levels, sub.render_levels = max(sub.levels, levels), max(sub.render_levels, levels)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def surface(body):
    bpy.context.view_layer.update()
    evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    tree = BVHTree.FromPolygons([body.matrix_world @ v.co for v in mesh.vertices],
                                [p.vertices[:] for p in mesh.polygons])
    evaluated.to_mesh_clear()
    return tree


def line(start, end, count, sizes):
    rng = random.Random(count)
    start, end = Vector(start), Vector(end)
    step = (end - start).length / max(count - 1, 1)
    points = []
    for index in range(count):
        t = index / max(count - 1, 1)
        offset = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0)) * step * 0.15
        points.append((start.lerp(end, t) + offset, (sizes[0] + (sizes[1] - sizes[0]) * t) * rng.uniform(0.85, 1.15)))
    return points


def finish(name, bm, along):
    layer = bm.verts.layers.float.new("along")
    for v in bm.verts:
        v[layer] = along(v)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = True
    return obj


def tube(bm, centres, radii, sides=12):
    rings = []
    for index, (centre, radius) in enumerate(zip(centres, radii)):
        heading = centres[min(index + 1, len(centres) - 1)] - centres[max(index - 1, 0)]
        frame = heading.to_track_quat("Z", "Y").to_matrix()
        rings.append([bm.verts.new(centre + frame @ Vector((math.cos(a) * radius, math.sin(a) * radius, 0)))
                      for a in (2 * math.pi * k / sides for k in range(sides))])
    for a, b in zip(rings, rings[1:]):
        for k in range(sides):
            bm.faces.new((a[k], a[(k + 1) % sides], b[(k + 1) % sides], b[k]))
    bm.faces.new(rings[-1])
    bm.faces.new(reversed(rings[0]))


def resample(chain, count):
    chain = [Vector(p) for p in chain]
    lengths = [0.0]
    for a, b in zip(chain, chain[1:]):
        lengths.append(lengths[-1] + (b - a).length)
    out = []
    for index in range(count):
        target = lengths[-1] * index / (count - 1)
        k = next((i for i in range(1, len(lengths)) if lengths[i] >= target), len(lengths) - 1)
        out.append(chain[k - 1].lerp(chain[k], (target - lengths[k - 1]) / (lengths[k] - lengths[k - 1] or 1.0)))
    return out


def horn(name, body, path, radius):
    path = [Vector(p) for p in path]
    if body is not None:
        hit = surface(body).find_nearest(path[0])[0]
        shift = hit - (path[1] - path[0]).normalized() * radius - path[0] if hit is not None else Vector()
        path = [p + shift for p in path]
    centres = resample(path, 25)
    radii = [radius * (1 - i / 24) ** 0.8 * (1.06 if i % 2 else 1.0) + radius * 0.03 for i in range(25)]
    bm = bmesh.new()
    tube(bm, centres, radii)
    base, length = centres[0], (centres[-1] - centres[0]).length or 1.0
    return finish(name, bm, lambda v: min((v.co - base).length / length, 1.0))


def piece(bm, kind, size, rng):
    if kind == "spike":
        tip = Vector((0, -rng.uniform(0.1, 0.3) * size, size))
        tube(bm, [Vector(), tip * 0.5 + Vector((0, 0, size * 0.1)), tip], [size * 0.35, size * 0.18, 0.0], 10)
        return
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=size * 0.5)
    stretch = rng.uniform(1.1, 1.4)
    for v in bm.verts:
        keel = size * 0.18 * max(0.0, 1 - abs(v.co.x) / (size * 0.2)) if v.co.z > 0 else 0.0
        v.co.z = v.co.z * (0.4 if v.co.z > 0 else 0.3) + keel
        v.co.y *= stretch


def stud(name, body, kind, points):
    if kind not in ("spike", "plate"):
        raise ValueError(f"kind must be spike or plate, got {kind}")
    rng, tree, bm, heights = random.Random(len(points)), surface(body), bmesh.new(), {}
    for location, size in points:
        hit, normal, _, _ = tree.find_nearest(Vector(location))
        if hit is None:
            continue
        part = bmesh.new()
        piece(part, kind, size, rng)
        sink = size * (0.25 if kind == "spike" else 0.05)
        bmesh.ops.transform(part, matrix=normal.to_track_quat("Z", "Y").to_matrix().to_4x4(), verts=part.verts)
        bmesh.ops.translate(part, vec=hit - normal * sink, verts=part.verts)
        for v in part.verts:
            heights[v.co.to_tuple(5)] = min(max((v.co - hit).dot(normal) / size, 0.0), 1.0)
        temp = bpy.data.meshes.new("temp")
        part.to_mesh(temp)
        part.free()
        bm.from_mesh(temp)
        bpy.data.meshes.remove(temp)
    return finish(name, bm, lambda v: heights.get(v.co.to_tuple(5), 0.0))
