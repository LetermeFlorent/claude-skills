import os
import sys

import bpy
import numpy as np

MARK = "@@ "


def args():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def say(text):
    print(MARK + str(text), flush=True)


def fail(text):
    say(f"failed: {text}")
    raise SystemExit(1)


def ext_of(path):
    return os.path.splitext(path)[1].lower().lstrip(".")


def globs(op):
    try:
        prop = op.get_rna_type().properties.get("filter_glob")
    except (AttributeError, KeyError, RuntimeError):
        return []
    return [part.strip().lstrip("*.").lower() for part in prop.default.split(";")] if prop else []


def importers():
    found = []
    for module in dir(bpy.ops):
        for name in dir(getattr(bpy.ops, module)):
            if "import" in name or module.startswith("import"):
                op = getattr(getattr(bpy.ops, module), name)
                found.append((f"{module}.{name}", op, globs(op)))
    return found


def importer(ext):
    found = importers()
    exact = [(idname, op) for idname, op, exts in found if ext in exts]
    near = [(idname, op) for idname, op, exts in found if any(e and ext.startswith(e) for e in exts)]
    hits = sorted(exact or near, key=lambda hit: not hit[0].startswith("wm."))
    return hits[0] if hits else (None, None)


def load(path):
    if not path or path == "-" or ext_of(path) == "blend":
        if not path or path == "-":
            bpy.ops.wm.read_factory_settings(use_empty=True)
        return
    bpy.ops.wm.read_factory_settings(use_empty=True)
    idname, op = importer(ext_of(path))
    if not op:
        fail(f"no importer in this Blender for .{ext_of(path)}")
    say(f"imported with bpy.ops.{idname}")
    op(filepath=os.path.abspath(path))


def image_on(ob, kind):
    for slot in ob.material_slots:
        tree = slot.material.node_tree if slot.material and slot.material.node_tree else None
        for node in tree.nodes if tree else []:
            target = "Base Color" if kind == "colour" else "Color"
            wanted = node.type == ("BSDF_PRINCIPLED" if kind == "colour" else "NORMAL_MAP")
            link = node.inputs[target].links[0] if wanted and node.inputs[target].links else None
            if link and link.from_node.type == "TEX_IMAGE" and link.from_node.image:
                image = link.from_node.image
                pixels = np.array(image.pixels[:]).reshape(image.size[1], image.size[0], image.channels)
                return pixels
    return None


def samples(bm, pixels):
    uv = bm.loops.layers.uv.active
    height, width = pixels.shape[:2]
    out = []
    for face in bm.faces:
        u, v = np.mean([loop[uv].uv[:] for loop in face.loops], 0) if uv else (0.5, 0.5)
        x, y = int(u % 1 * (width - 1)), int(v % 1 * (height - 1))
        out.append((face.normal.z, pixels[y, x, :3]))
    return out
