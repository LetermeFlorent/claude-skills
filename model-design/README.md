# model-design

To install it, see `INSTALL.md` at the root of the repository.

Loads by itself before an agent models a creature, character, animal, vehicle or object in 3D. Instead of
inventing the shape while modeling, the agent first writes a design sheet: references, silhouette,
proportions as numbers, masses, joints, surfaces and a checklist. Then it builds in three passes, large
shapes first, details last, and checks each pass with captures and measured proportions before going on.
It works with the blender-3d skill, which does the actual building in Blender.

Files:

- `SKILL.md`: the design sheet slots, the three passes and the rules during the build.
- `reference/proportions.md`: starting proportions for humans, four-legged animals, reptiles, birds, bat
  wings, wyverns and everyday objects.
- `reference/forms.md`: the body masses that make a creature look alive, and real surfaces to copy
  (scales, armour plates, wing membrane, horn, wear).

## What was tested

Runs made while writing the skill, from the reports and captures they left:

- The same original wyvern-like monster was asked from an empty scene, with the blender-3d skill, by a
  small model (Haiku, high effort) and a mid model (Sonnet, low effort).
- With this skill, the small model wrote a complete design sheet: references, silhouette, proportions,
  joints and surfaces. Its build stayed weak: boxy faceted body, wings made of a few flat triangles, one
  wavy pattern on every part, few blob-like plates, flat horns. The minimums in the rules section and
  the creature kit of blender-3d were added from that run.
- A run with the minimums and the kit is under way; its result is not in this section yet.
