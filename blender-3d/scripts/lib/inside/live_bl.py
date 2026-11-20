import contextlib
import io
import os
import runpy
import sys
import traceback

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy
from util import args

QUEUE = args()[0]
INBOX = os.path.join(QUEUE, "in")
OUTBOX = os.path.join(QUEUE, "out")
STOP = os.path.join(QUEUE, "stop")
TICK = 0.3


def view3d():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                region = next(r for r in area.regions if r.type == "WINDOW")
                return {"window": window, "area": area, "region": region}
    return {}


def execute(path):
    buffer = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        try:
            with bpy.context.temp_override(**view3d()):
                runpy.run_path(path, run_name="__main__")
        except SystemExit as stop:
            code = stop.code if isinstance(stop.code, int) else int(bool(stop.code))
        except Exception:
            traceback.print_exc()
            code = 1
    return code, buffer.getvalue()


def redraw():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()


def material_view():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.shading.type = "MATERIAL"
    return None


def tick():
    if os.path.exists(STOP):
        os.remove(STOP)
        bpy.ops.wm.quit_blender()
        return None
    for name in sorted(n for n in os.listdir(INBOX) if n.endswith(".py")):
        path = os.path.join(INBOX, name)
        code, output = execute(path)
        os.remove(path)
        temporary = os.path.join(OUTBOX, name + ".part")
        with open(temporary, "w", encoding="utf-8") as result:
            result.write(f"{output}\n@@exit {code}\n")
        os.replace(temporary, os.path.join(OUTBOX, name + ".txt"))
        redraw()
    return TICK


os.makedirs(INBOX, exist_ok=True)
os.makedirs(OUTBOX, exist_ok=True)
bpy.app.timers.register(material_view, first_interval=TICK)
bpy.app.timers.register(tick, first_interval=TICK, persistent=True)
with open(os.path.join(QUEUE, "ready"), "w", encoding="utf-8") as ready:
    ready.write(str(os.getpid()))
