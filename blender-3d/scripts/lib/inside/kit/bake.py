import math
import os

import bpy
import numpy

PASSES = (("color", "DIFFUSE", "sRGB"), ("rough", "ROUGHNESS", "Non-Color"), ("normal", "NORMAL", "Non-Color"))


def only(obj):
    for other in bpy.context.view_layer.objects:
        other.select_set(other == obj)
    bpy.context.view_layer.objects.active = obj


def unwrap(obj):
    only(obj)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")


def bake_pass(obj, nodes, name, kind):
    label, bake_type, space = kind
    image = bpy.data.images.new(f"{name}_{label}", 2048, 2048, alpha=False)
    image.colorspace_settings.name = space
    node = nodes.new("ShaderNodeTexImage")
    node.image = image
    nodes.active = node
    only(obj)
    if bake_type == "DIFFUSE":
        bpy.ops.object.bake(type=bake_type, pass_filter={"COLOR"}, margin=16)
    else:
        bpy.ops.object.bake(type=bake_type, margin=16)
    return image


def rewire(material, images):
    tree = material.node_tree
    tree.nodes.clear()
    shader = tree.nodes.new("ShaderNodeBsdfPrincipled")
    color, rough, normal = (tree.nodes.new("ShaderNodeTexImage") for _ in range(3))
    color.image, rough.image, normal.image = images
    normal_map = tree.nodes.new("ShaderNodeNormalMap")
    tree.links.new(color.outputs["Color"], shader.inputs["Base Color"])
    tree.links.new(rough.outputs["Color"], shader.inputs["Roughness"])
    tree.links.new(normal.outputs["Color"], normal_map.inputs["Color"])
    tree.links.new(normal_map.outputs["Normal"], shader.inputs["Normal"])
    tree.links.new(shader.outputs["BSDF"], tree.nodes.new("ShaderNodeOutputMaterial").inputs["Surface"])


def sheet(images, path):
    tiles = []
    for image in images:
        small = image.copy()
        small.scale(256, 256)
        tiles.append(numpy.array(small.pixels[:], dtype=numpy.float32).reshape(256, 256, 4))
        bpy.data.images.remove(small)
    while len(tiles) % 3:
        tiles.append(numpy.zeros((256, 256, 4), dtype=numpy.float32))
    rows = [numpy.concatenate(tiles[i:i + 3], axis=1) for i in range(0, len(tiles), 3)]
    grid = numpy.concatenate(rows[::-1], axis=0)
    out = bpy.data.images.new("sheet", grid.shape[1], grid.shape[0])
    out.pixels = grid.ravel()
    out.filepath_raw, out.file_format = path, "PNG"
    out.save()
    bpy.data.images.remove(out)


def bake(objects, folder):
    os.makedirs(folder, exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine, scene.cycles.samples = "CYCLES", 16
    baked = []
    for obj in objects:
        if not obj.data.uv_layers:
            unwrap(obj)
        material = obj.active_material.copy()
        obj.active_material = material
        images = [bake_pass(obj, material.node_tree.nodes, obj.name, kind) for kind in PASSES]
        for image in images:
            image.filepath_raw, image.file_format = os.path.join(folder, image.name + ".png"), "PNG"
            image.save()
        rewire(material, images)
        baked += images
    sheet(baked, os.path.join(folder, "sheet.png"))
    print(f"baked {len(baked)} images, all in one view: {os.path.join(folder, 'sheet.png')}")
    return baked
