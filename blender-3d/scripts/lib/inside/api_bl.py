import importlib
import inspect
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy
from util import args, say

TREES = ("ShaderNodeTree", "GeometryNodeTree", "CompositorNodeTree", "TextureNodeTree")
LIMIT = 80
ITEMS = 40


def default(prop):
    if prop.type == "ENUM":
        items = [item.identifier for item in prop.enum_items]
        items = items if len(items) <= ITEMS else f"{len(items)} items, see the API page"
        shown = prop.default_flag if prop.is_enum_flag else prop.default
        return f"{shown or '-'} of {items or 'items set at run time'}"
    if prop.type in {"POINTER", "COLLECTION"}:
        return prop.fixed_type.identifier
    if getattr(prop, "is_array", False) and prop.array_length:
        return tuple(round(v, 4) if isinstance(v, float) else v for v in prop.default_array)
    return getattr(prop, "default", "")


def prop_lines(rna, inherited=()):
    for prop in rna.properties:
        if prop.identifier == "rna_type" or prop.identifier in inherited:
            continue
        flags = " read-only" if prop.is_readonly else ""
        kind = f"{prop.type.lower()} {prop.subtype.lower()}"
        yield f"  {prop.identifier}: {kind} = {default(prop)}{flags} | {prop.description}"


def show_op(path):
    module, name = path.split(".")[-2:]
    rna = getattr(getattr(bpy.ops, module), name).get_rna_type()
    say(f"operator bpy.ops.{module}.{name}: {rna.description}")
    for line in prop_lines(rna):
        say(line)


def sockets(name):
    for kind in TREES:
        tree = bpy.data.node_groups.new("api_probe", kind)
        try:
            node = tree.nodes.new(name)
        except RuntimeError:
            bpy.data.node_groups.remove(tree)
            continue
        for side, socks in (("input", node.inputs), ("output", node.outputs)):
            for sock in socks:
                value = getattr(sock, "default_value", None)
                if hasattr(value, "__len__") and not isinstance(value, str):
                    value = tuple(round(v, 4) for v in value)
                say(f"  {side} {sock.identifier} '{sock.name}': {sock.type.lower()} = {value}")
        say(f"  node tree type {kind}")
        bpy.data.node_groups.remove(tree)
        return


def show_type(name):
    cls = getattr(bpy.types, name)
    rna = cls.bl_rna
    base = rna.base.identifier if rna.base else "-"
    say(f"type bpy.types.{name} (base {base}, its members not repeated): {rna.description}")
    for line in prop_lines(rna, rna.base.properties.keys() if rna.base else ()):
        say(line)
    inherited = rna.base.functions.keys() if rna.base else ()
    for func in [f for f in rna.functions if f.identifier not in inherited]:
        params = ", ".join(p.identifier for p in func.parameters)
        say(f"  def {func.identifier}({params}) | {func.description}")
    if issubclass(cls, bpy.types.Node):
        sockets(name)


def search(word):
    word = word.lower()
    hits = []
    for module in dir(bpy.ops):
        for name in dir(getattr(bpy.ops, module)):
            try:
                text = getattr(getattr(bpy.ops, module), name).get_rna_type().description
            except (AttributeError, KeyError, RuntimeError):
                text = ""
            if word in f"{module}.{name} {text}".lower():
                hits.append(f"bpy.ops.{module}.{name} | {text}")
    for name in dir(bpy.types):
        rna = getattr(getattr(bpy.types, name), "bl_rna", None)
        if rna and word in f"{name} {rna.name} {rna.description}".lower():
            hits.append(f"bpy.types.{name} | {rna.description}")
    for hit in hits[:LIMIT]:
        say(hit)
    say(f"{len(hits)} matches for '{word}'" + (f", first {LIMIT} shown" if len(hits) > LIMIT else ""))


def python_object(path):
    parts = path.split(".")
    for cut in range(len(parts), 0, -1):
        try:
            found = importlib.import_module(".".join(parts[:cut]))
        except ImportError:
            continue
        for part in parts[cut:]:
            found = getattr(found, part, None)
        return found
    return None


def show_python(path, found):
    try:
        signature = str(inspect.signature(found))
    except (TypeError, ValueError):
        signature = ""
    say(f"python {path}{signature}")
    for line in (inspect.getdoc(found) or "no docstring").splitlines():
        say(f"  {line}")
    browsable = inspect.ismodule(found) or inspect.isclass(found)
    members = [m for m in dir(found) if not m.startswith("_")] if browsable else []
    if members:
        say("  members: " + ", ".join(members))


def main():
    query = (args() or [""])[0]
    say(f"blender {bpy.app.version_string}")
    if not query:
        return
    name = query.removeprefix("bpy.types.")
    if query.startswith("bpy.ops."):
        show_op(query)
    elif hasattr(bpy.types, name):
        show_type(name)
    elif "." in query and python_object(query) is not None:
        show_python(query, python_object(query))
    else:
        search(query)


main()
