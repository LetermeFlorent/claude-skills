import os
import sys

import bpy

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
