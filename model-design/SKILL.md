---
name: model-design
description: Use when a 3D creature, character, animal, monster, vehicle or prop is about to be modeled in Blender or any 3D tool, when a request says realistic, ultra realistic, from imagination or "in the style of", when a model looks like spheres and cylinders stuck together, has wrong proportions, stiff tube limbs, an unreadable silhouette, evenly sized details or parts floating off the body.
---

# Model design

A model built straight from words comes out as primitives stuck together: the shape is invented while
modeling. This skill writes the design first, as numbers and lists, then builds from the largest forms to
the smallest, checking each level before the next. It pairs with the blender-3d skill, which does the
building, captures and export.

## 1. Design sheet before any geometry

Write `<work>/design.md` before the first mesh. No vertex is created while one of these slots is empty.

| Slot | What goes in it |
|---|---|
| Request | user's words, style word, use (game, render, print), polygon budget |
| References | user's images opened and described; otherwise 2 or 3 real animals or objects, each lending named parts (wings of a bat, hide of a crocodile, legs of an ostrich) |
| Silhouette | side, front and top outline in one line each; the one feature read first from far away |
| Proportions | table in head lengths (or wheel, seat, handle for objects), copied from `reference/proportions.md` then changed on purpose, each change with its reason |
| Masses | primary (torso, pelvis, head, neck, tail), secondary (shoulders, thighs, jaw, brow, muscle groups), tertiary (scales, plates, spikes, scars, teeth), each tertiary row with its count and size range |
| Joints | every place that bends, in order from root to tip, for the rig |
| Surfaces | per zone: real reference material, pattern, colour, roughness, relief |
| Checklist | every line above as a thing that can be seen on a capture |

Read `reference/proportions.md` when filling Proportions and Joints, `reference/forms.md` when filling
Masses and Surfaces.

## 2. Build from large to small

Three passes, each closed by captures from front, side, top and three-quarter before the next starts.

1. Blockout: primary masses only, grey, one mesh. Measure each part with the blender-3d `info.py` sizes
   and divide by the head length: every ratio within 10 % of the Proportions table, or the table changed
   with its reason. Side capture laid next to the Silhouette line: same outline, or fix now.
2. Secondary: muscles, joint bulges, jaw, brow, ribcage, belly sag. Limbs taper from body to tip and swell
   at every joint; no limb keeps one radius along its length.
3. Tertiary: details sized in three classes (large few, medium some, small many, about 60/30/10 of the
   surface), grouped where the real reference has them, never spread evenly. Every piece touches the
   surface it grows from.

## 3. Rules that hold during the build

These hold in every pass.

- A detail is never added to fix a primary or secondary problem: wrong mass gets fixed at its level.
- Weight sits over the feet: centre of the body above the area between them, legs angled to carry it.
- Nothing perfectly symmetric or regular in the final pass: sizes, spacing and angles vary a little.
- A part that looks wrong twice goes back to the design sheet, not to more tweaking.
- After every capture, write the three worst defects seen, then fix the worst before any new part.
- Minimums, each refused when a capture shows it: a flat facet or box edge on the body (Subdivision 2
  or more, smooth shading); a wing membrane of a few big triangles (12 rows or more, sagging between the
  fingers); one pattern on every part, or Wave stripes on hide; plates or spikes fewer than the count the
  design sheet gives per row, or all the same size; body colour without a lighter belly and darker back;
  a horn as a flat or straight cone (taper, curve and ring loops); back plates narrower than a quarter of
  the torso width, or a wingspan shorter than the body from snout to tail tip (wings that are also forelegs
  count it with the fingers spread).
- Blockout ratios come from the chain lengths and widths the blender-3d kit `body()` prints, never from
  the overall box of the mesh; a leg is measured from the hip or shoulder joint, pelvis
  and shoulder blade left out.
- Report names the design sheet, each ratio measured against its target, and every checklist line kept
  or missed.
