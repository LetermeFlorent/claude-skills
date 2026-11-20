# Building a creature: methods that work

Read before the first mesh of a creature. Each part below shows the method, the trap that breaks it and
a short example to adapt. Write your own script from it: names, sizes and counts come from the design
sheet, never from these examples.

## Body: one skinned mesh from joint chains

Write the skeleton as named chains of `(point, radius)`, root to tip: torso, neck, head, tail, each leg,
each wing arm. Chains that meet share the exact same point, so the Skin modifier joins them into one body.

```python
chains = {"torso": [((0, 0, 1), 0.55), ((0.5, 0, 1.15), 0.62)], "neck": [((0.5, 0, 1.15), 0.62), ...]}
points, edges = [], set()
for joints in chains.values():
    ids = []
    for location, radius in joints:
        hit = next((i for i, p in enumerate(points) if (p[0] - Vector(location)).length < 1e-4), None)
        if hit is None:
            points.append((Vector(location), radius))
            hit = len(points) - 1
        ids.append(hit)
    edges.update(tuple(sorted(pair)) for pair in zip(ids, ids[1:]))
mesh = bpy.data.meshes.new("Body")
mesh.from_pydata([p.to_tuple() for p, _ in points], sorted(edges), [])
body = bpy.data.objects.new("Body", mesh)
bpy.context.collection.objects.link(body)
body.modifiers.new("Skin", "SKIN")
for vertex, (_, radius) in zip(mesh.skin_vertices[0].data, points):
    vertex.radius = (radius, radius * 0.9)
mesh.skin_vertices[0].data[0].use_root = True
sub = body.modifiers.new("Subdivision", "SUBSURF")
sub.levels = sub.render_levels = 2
for poly in body.data.polygons:
    poly.use_smooth = True
```

- Radii change gently from one joint to the next (at most about 1.5 times): a jump makes balloon bulges.
- Add a joint at every bend and one between joints on long chains, so the limb tapers and the rig bends.
- Measure each chain: its length and widest radius divided by the head chain length give the ratios to
  compare with the design sheet. The overall box of the mesh says nothing about proportions.
- Subdivision level 1 leaves the box edges of the Skin modifier visible: always 2.

## Parts placed on the surface

Plates, spikes, horns and claws are their own meshes, placed on the evaluated body (after Skin and
Subdivision), turned to its normal and sunk in a little, so none floats.

```python
bpy.context.view_layer.update()
evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
temp = evaluated.to_mesh()
tree = BVHTree.FromPolygons([body.matrix_world @ v.co for v in temp.vertices], [p.vertices[:] for p in temp.polygons])
evaluated.to_mesh_clear()
hit, normal, _, _ = tree.find_nearest(Vector(guess))
place = Matrix.Translation(hit - normal * size * 0.25) @ normal.to_track_quat("Z", "Y").to_matrix().to_4x4()
```

- Rows along the spine: points between two ends, size growing or shrinking along the row, each spacing,
  size and angle varied by about 15 %. Back plates at least a quarter of the torso width.
- A plate is a flattened sphere with a raised keel along its middle; a spike is a cone bent slightly
  backwards; join all pieces of one kind into one mesh.

## Horns, claws, teeth, tail blades: a tube along a path

Rings of vertices along a path of 3 or more points, radius shrinking to the tip, every second ring
slightly wider: the ring loops give the growth rings their relief. Store a float attribute `along`
(0 at the base, 1 at the tip) for the material.

```python
layer = bm.verts.layers.float.new("along")
for index, centre in enumerate(centres):
    radius = base_radius * (1 - index / last) ** 0.8 * (1.06 if index % 2 else 1.0)
    frame = (centres[min(index + 1, last)] - centres[max(index - 1, 0)]).to_track_quat("Z", "Y").to_matrix()
    ring = [bm.verts.new(centre + frame @ Vector((cos(a) * radius, sin(a) * radius, 0))) for a in angles]
```

Bridge each ring to the next with quads, cap the tip, sink the base into the body.

## Wing membrane: a grid between bone chains

Chains = body edge, then each finger, root to tip. Resample each chain to 16 points, then fill a grid
between neighbour chains: 8 columns per gap. Pull the trailing edge inward between fingers (scallop) and
let the middle sag along the normal (slack). Weld vertices that coincide at the root and dissolve
degenerate faces, or the glTF exporter calls the mesh invalid after rigging. Add a Solidify of a few
millimetres.

```python
inward = (left[0].lerp(right[0], u) - point) * 0.25 * sin(pi * u) * t ** 2
slack = 0.04 * sin(pi * u) * sin(pi * t) * (left[r] - right[r]).length
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
```

## Rig, in this order

The body must stay a Skin mesh until the bones exist, and become a real mesh before UVs.

1. Place every part first: the rig comes last.
2. `bpy.ops.object.skin_armature_create(modifier="Skin")` with the body selected and active: one bone per
   edge.
3. Remove the Armature modifier it added and clear the body's vertex groups, then apply Skin and
   Subdivision: the body becomes a real mesh with faces, needed for UVs and baking.
4. Delete vertices with no face left (`not v.link_faces`): they count as extra parts.
5. Parent the body and every other mesh to the armature with `ARMATURE_AUTO`, then `mesh.validate()` on
   each.
6. Pose neck, tail, a leg and a wing, capture, check nothing tears, reset the pose.

## Materials: one real pattern per surface

Object coordinates through a Mapping node scaled by `1 / cell`, `cell` = pattern size in metres (hide:
about a twelfth of the torso width). Each recipe gives three values: crevice (dark, rough), height (to a
Bump node, strength 0.8, distance `cell * 0.15`) and zone (light colour mix).

| Surface | Crevice | Height | Zone |
|---|---|---|---|
| Hide | Voronoi distance to edge, 0 to 0.09 mapped 1 to 0, plus a second Voronoi at 3 times the scale | edge distance minus crevice | belly: geometry normal Z, -0.7 to 0.1 mapped 1 to 0 |
| Plate | Voronoi distance to edge, 0 to 0.07 mapped 1 to 0 | Voronoi F1 dome times edge distance, minus stretched noise scratches | worn rims near the edges |
| Membrane | ridged noise: `abs(noise - 0.5)` 0 to 0.03 mapped 1 to 0, on coordinates warped by noise; a finer copy at half weight | veins plus fine wrinkle noise | slow noise; Subsurface weight 0.35, bump strength 0.4 |
| Keratin | `sine(along * 70 + noise)` rings | rings plus grooves noise | `along`: dark base, pale tip |

Colour = mix(crevice, mix(zone, mid colour varied by large noise, light colour), dark colour). Roughness
from crevice, 0.45 to 0.85 (keratin from 0.3). Wave texture stripes are wood, never hide.

## Bake

For each mesh: copy its material (two meshes sharing one material overwrite each other's bake), smart UV
project (66 degrees, margin 0.02) where it has no UVs, then bake `DIFFUSE` with `pass_filter={"COLOR"}`,
`ROUGHNESS` and `NORMAL` into new 2048 images (colour sRGB, the other two Non-Color), the image node
selected and active in the material each time. Save every image, then rebuild the material from the
three images (normal through a Normal Map node). To look at many maps at once, scale copies to 256 pixels
and tile them into one sheet image with numpy, then open the sheet.
