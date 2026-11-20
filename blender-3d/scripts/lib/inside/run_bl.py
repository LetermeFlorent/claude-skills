import contextlib
import os
import runpy
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy
from util import MARK, args, load, say


class Marked:
    def __init__(self, stream):
        self.stream, self.pending = stream, ""

    def write(self, text):
        self.pending += text
        *lines, self.pending = self.pending.split("\n")
        for line in lines:
            self.stream.write(MARK + line + "\n")
        return len(text)

    def flush(self):
        if self.pending:
            self.stream.write(MARK + self.pending + "\n")
            self.pending = ""
        self.stream.flush()


script, save, source = args()[:3]
load(source)
marked = Marked(sys.stdout)
with contextlib.redirect_stdout(marked):
    runpy.run_path(script, run_name="__main__")
marked.flush()
if save:
    bpy.ops.wm.save_as_mainfile(filepath=save, copy=True)
    say(f"saved: {save}")
