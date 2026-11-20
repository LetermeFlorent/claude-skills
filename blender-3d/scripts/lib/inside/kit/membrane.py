import math

import bmesh

from .parts import finish, resample


def membrane(name, chains):
    if len(chains) < 2:
        raise ValueError("membrane needs two bone chains or more: body edge first, then each finger")
    rows, columns, lines = 16, 8, [resample(chain, 16) for chain in chains]
    bm, grid = bmesh.new(), []
    for left, right in zip(lines, lines[1:]):
        for c in range(0 if not grid else 1, columns + 1):
            u, column = c / columns, []
            for r in range(rows):
                t, point = r / (rows - 1), left[r].lerp(right[r], u)
                inward = (left[0].lerp(right[0], u) - point) * 0.25 * math.sin(math.pi * u) * t ** 2
                normal = (right[r] - left[r]).cross(left[min(r + 1, rows - 1)] - left[max(r - 1, 0)]).normalized()
                slack = 0.04 * math.sin(math.pi * u) * math.sin(math.pi * t) * (left[r] - right[r]).length
                column.append(bm.verts.new(point + inward + normal * slack))
            grid.append(column)
    for a, b in zip(grid, grid[1:]):
        for r in range(rows - 1):
            bm.faces.new((a[r], b[r], b[r + 1], a[r + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = finish(name, bm, lambda v: 0.0)
    obj.modifiers.new("Solidify", "SOLIDIFY").thickness = 0.006
    return obj
