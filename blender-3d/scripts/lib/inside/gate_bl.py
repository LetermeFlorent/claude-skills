import colorsys
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bmesh
import bpy
import numpy as np
from util import args, fail, image_on, load, samples, say

WELD = 1e-4


def world_bm(name):
    ob = bpy.data.objects.get(name)
    if ob is None or ob.type != "MESH":
        names = ", ".join(sorted(o.name for o in bpy.data.objects if o.type == "MESH"))
        fail(f"no mesh named {name}; meshes: {names}")
    deps = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    bm.from_object(ob, deps)
    bm.transform(ob.matrix_world)
    return ob, bm


def pieces(bm):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=WELD)
    bm.verts.ensure_lookup_table()
    seen, found = set(), []
    for start in bm.verts:
        if start.index in seen:
            continue
        group, stack = [], [start]
        seen.add(start.index)
        while stack:
            vert = stack.pop()
            group.append(vert)
            for edge in vert.link_edges:
                other = edge.other_vert(vert)
                if other.index not in seen:
                    seen.add(other.index)
                    stack.append(other)
        found.append(group)
    return [np.array([v.co[:] for v in group]) for group in found if len(group) > 3], found


def frame(points):
    axis = 0 if np.ptp(points[:, 0]) >= np.ptp(points[:, 1]) else 1
    slices = np.digitize(points[:, axis], np.linspace(points[:, axis].min(), points[:, axis].max(), 21))
    widths = [np.ptp(points[slices == s, 1 - axis]) for s in set(slices) if (slices == s).sum() > 3]
    return np.ptp(points[:, axis]), float(np.percentile(widths, 70))


def body_measures(name):
    ob, bm = world_bm(name)
    angles = [np.degrees(e.calc_face_angle(0)) for e in bm.edges if len(e.link_faces) == 2]
    say(f"measure body_bend {name} {np.median(angles):.3f}")
    colour, normal = image_on(ob, "colour"), image_on(ob, "normal")
    if colour is None or normal is None:
        say(f"no baked colour or normal image on {name}")
        for key in ("belly", "saturation", "relief"):
            say(f"measure {key} {name} 0")
    else:
        hits = samples(bm, colour)
        light = lambda rows: float(np.mean([c.mean() for _, c in rows])) if rows else 0.0
        belly, back = light([h for h in hits if h[0] < -0.5]), light([h for h in hits if h[0] > 0.5])
        say(f"measure belly {name} {belly / max(back, 1e-6):.3f}")
        sat = np.mean([colorsys.rgb_to_hsv(*c)[1] for _, c in hits])
        say(f"measure saturation {name} {sat:.3f}")
        say(f"measure relief {name} {np.std([c[0] for _, c in samples(bm, normal)]):.3f}")
    points, _ = pieces(bm)
    whole = np.vstack(points)
    bm.free()
    return whole


def wing_measures(names, body):
    length, width = frame(body)
    reach = 0.0
    for name in names:
        _, bm = world_bm(name)
        parts, groups = pieces(bm)
        for index, (points, group) in enumerate(zip(parts, groups)):
            tris = sum(len(f.verts) - 2 for f in {f for v in group for f in v.link_faces})
            say(f"measure wing_tris {name}.{index} {tris}")
            reach += float(np.ptp((points - points.mean(0)) @ np.linalg.svd(points - points.mean(0))[2][0]))
        bm.free()
    say(f"measure wingspan wings {(reach + width) / length:.3f}")


def row_measures(name, body, plate):
    _, width = frame(body)
    _, bm = world_bm(name)
    parts, _ = pieces(bm)
    say(f"measure count {name} {len(parts)}")
    sizes = [np.linalg.norm(np.ptp(p, 0)) for p in parts]
    say(f"measure spread {name} {np.std(sizes) / max(np.mean(sizes), 1e-6):.3f}")
    if plate:
        axis = 0 if np.ptp(body[:, 0]) >= np.ptp(body[:, 1]) else 1
        widest = max(np.ptp(p[:, 1 - axis]) for p in parts)
        say(f"measure plate_width {name} {widest / width:.3f}")
    bm.free()


def horn_measures(name):
    _, bm = world_bm(name)
    for index, points in enumerate(pieces(bm)[0]):
        centred = points - points.mean(0)
        main = np.linalg.svd(centred, full_matrices=False)[2][0]
        along = centred @ main
        cuts = np.linspace(along.min(), along.max(), 11)
        mids = [centred[(along >= a) & (along <= b)].mean(0) for a, b in zip(cuts, cuts[1:])
                if ((along >= a) & (along <= b)).any()]
        chord = mids[-1] - mids[0]
        length = max(np.linalg.norm(chord), 1e-6)
        bend = max(np.linalg.norm(np.cross(m - mids[0], chord)) / length for m in mids)
        say(f"measure horn_curve {name}.{index} {bend / length:.3f}")
    bm.free()


def main():
    source, plan = args()[0], json.loads(args()[1])
    load(source)
    body = body_measures(plan["body"])
    if plan["wings"]:
        wing_measures(plan["wings"], body)
    for name in plan["plates"] + plan["spikes"]:
        row_measures(name, body, name in plan["plates"])
    for name in plan["horns"]:
        horn_measures(name)


main()
