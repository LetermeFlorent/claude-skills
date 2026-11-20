import math
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy
from mathutils import Vector
from util import args, fail, load, say

VIEWS = {"front": (0, -90), "back": (0, 90), "left": (0, 180), "right": (0, 0), "side": (0, 0),
         "top": (89.9, -90), "bottom": (-89.9, -90), "three_quarter": (30, -45)}
ZOOM, FOCUS = float(args()[6]), args()[7]
SHAPES = {"MESH", "CURVE", "SURFACE", "META", "FONT", "CURVES", "POINTCLOUD", "VOLUME", "GREASEPENCIL"}


def direction(view):
    elevation, azimuth = VIEWS[view] if view in VIEWS else map(float, view.split(":"))
    el, az = math.radians(elevation), math.radians(azimuth)
    return Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))


def bounds():
    objects = bpy.context.scene.objects
    shown = [o for o in objects if o.type in SHAPES and not o.hide_render] or list(objects)
    if FOCUS:
        names = ", ".join(sorted(o.name for o in shown))
        shown = [o for o in shown if o.name == FOCUS] or fail(f"no object named {FOCUS}; names: {names}")
    deps = bpy.context.evaluated_depsgraph_get()
    corners = [o.matrix_world @ Vector(c) for o in shown for c in o.evaluated_get(deps).bound_box]
    if not corners:
        fail("nothing to capture: the scene has no object")
    low = Vector(tuple(min(c[i] for c in corners) for i in range(3)))
    high = Vector(tuple(max(c[i] for c in corners) for i in range(3)))
    return (low + high) / 2, max((high - low).length / 2, 1e-3)


def set_engine(scene, name):
    for engine in (name.upper(), f"BLENDER_{name.upper()}"):
        try:
            scene.render.engine = engine
            return engine
        except TypeError:
            continue
    fail(f"unknown engine {name} in this Blender")


def node_colours():
    for material in bpy.data.materials:
        nodes = material.node_tree.nodes if material.node_tree else []
        for node in nodes:
            colour = node.inputs.get("Base Color") if node.type == "BSDF_PRINCIPLED" else None
            if colour and not colour.is_linked:
                material.diffuse_color = colour.default_value
                break


def prepare(scene, engine, size):
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    if engine == "BLENDER_WORKBENCH":
        scene.display.shading.light = "STUDIO"
        scene.display.shading.color_type = "TEXTURE"
        node_colours()
    elif engine == "CYCLES":
        scene.cycles.samples = 32
    if engine != "BLENDER_WORKBENCH" and not any(o.type == "LIGHT" for o in scene.objects):
        sun = bpy.data.objects.new("shots_sun", bpy.data.lights.new("shots_sun", "SUN"))
        sun.data.energy = 3
        sun.rotation_euler = (math.radians(50), 0, math.radians(30))
        scene.collection.objects.link(sun)
    if scene.world is None:
        scene.world = bpy.data.worlds.new("shots_world")
        scene.world.color = (0.4, 0.4, 0.4)


def camera(scene):
    cam = bpy.data.objects.new("shots_camera", bpy.data.cameras.new("shots_camera"))
    scene.collection.objects.link(cam)
    scene.camera = cam
    return cam


def shoot(scene, cam, view, path):
    center, radius = bounds()
    facing = direction(view)
    distance = radius / math.sin(cam.data.angle / 2) * 1.1 / ZOOM
    cam.location = center + facing * distance
    cam.rotation_euler = (-facing).to_track_quat("-Z", "Y").to_euler()
    cam.data.clip_start = max(distance - radius * 2, distance / 1000)
    cam.data.clip_end = distance + radius * 2
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    say(f"shot {view} {path}")


def main():
    source, out_dir, engine_name, views, size, prefix = args()[:6]
    load(source)
    scene = bpy.context.scene
    engine = set_engine(scene, engine_name)
    prepare(scene, engine, int(size))
    cam = camera(scene)
    os.makedirs(out_dir, exist_ok=True)
    for view in views.split(","):
        name = view.replace(":", "_")
        shoot(scene, cam, view, os.path.join(out_dir, f"{prefix}{name}.png"))
    say(f"engine {engine} views {views}")


main()
