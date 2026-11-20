import bmesh
from mathutils.bvhtree import BVHTree

WELD = 1e-5
SAMPLES = 1500
TOLERANCE = 0.002


def islands(bm):
    seen, found = set(), []
    for start in bm.faces:
        if start.index in seen:
            continue
        group, stack = [], [start]
        seen.add(start.index)
        while stack:
            face = stack.pop()
            group.append(face)
            for edge in face.edges:
                for other in edge.link_faces:
                    if other.index not in seen:
                        seen.add(other.index)
                        stack.append(other)
        found.append(group)
    return found


def pieces(ob, deps):
    evaluated = ob.evaluated_get(deps)
    bm = bmesh.new()
    bm.from_mesh(evaluated.to_mesh())
    bm.transform(ob.matrix_world)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=WELD)
    bm.faces.index_update()
    found = []
    for number, group in enumerate(islands(bm)):
        verts = list({v.index: v.co.copy() for face in group for v in face.verts}.items())
        index = {old: new for new, (old, _) in enumerate(verts)}
        polygons = [[index[v.index] for v in face.verts] for face in group]
        coords = [co for _, co in verts]
        label = ob.name if number == 0 else f"{ob.name} part {number + 1}"
        found.append((label, coords, BVHTree.FromPolygons(coords, polygons)))
    bm.free()
    evaluated.to_mesh_clear()
    return found


def gap(piece, others, tolerance):
    _, coords, tree = piece
    step = max(1, len(coords) // SAMPLES)
    best = float("inf")
    for _, _, other in others:
        if tree.overlap(other):
            return 0.0
        for co in coords[::step]:
            hit = other.find_nearest(co)
            if hit[3] is not None and hit[3] < best:
                best = hit[3]
                if best <= tolerance:
                    return best
    return best


def floating(objects, deps, size):
    found = [p for ob in objects if ob.type == "MESH" for p in pieces(ob, deps)]
    tolerance = size * TOLERANCE
    if len(found) < 2:
        return []
    result = []
    for piece in found:
        distance = gap(piece, [p for p in found if p is not piece], tolerance)
        if distance > tolerance:
            result.append((piece[0], distance))
    return result
