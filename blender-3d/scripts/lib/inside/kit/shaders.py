import bpy

PALETTES = {
    "hide": ((0.10, 0.08, 0.06), (0.30, 0.24, 0.17), (0.62, 0.55, 0.42)),
    "plate": ((0.03, 0.03, 0.03), (0.16, 0.13, 0.10), (0.45, 0.40, 0.33)),
    "membrane": ((0.12, 0.03, 0.02), (0.38, 0.12, 0.08), (0.55, 0.30, 0.22)),
    "keratin": ((0.04, 0.03, 0.03), (0.18, 0.14, 0.10), (0.70, 0.64, 0.52)),
}


class Tree:
    def __init__(self, material):
        material.node_tree.nodes.clear()
        self.nodes, self.links = material.node_tree.nodes, material.node_tree.links

    def add(self, kind, **values):
        node = self.nodes.new(kind)
        for key, value in values.items():
            if hasattr(node, key):
                setattr(node, key, value)
            else:
                node.inputs[key].default_value = value
        return node

    def link(self, out, node, socket):
        self.links.new(out, next(s for s in node.inputs if socket in (s.identifier, s.name)))

    def voronoi(self, vector, scale, feature="F1"):
        node = self.add("ShaderNodeTexVoronoi", feature=feature, Scale=scale)
        self.link(vector, node, "Vector")
        return node.outputs["Distance"]

    def noise(self, vector, scale, detail=8.0):
        node = self.add("ShaderNodeTexNoise", Scale=scale, Detail=detail)
        self.link(vector, node, "Vector")
        return node.outputs["Fac"]

    def remap(self, value, span, to=(0.0, 1.0)):
        node = self.add("ShaderNodeMapRange", clamp=True)
        node.inputs["From Min"].default_value, node.inputs["From Max"].default_value = span
        node.inputs["To Min"].default_value, node.inputs["To Max"].default_value = to
        self.link(value, node, "Value")
        return node.outputs["Result"]

    def math(self, operation, a, b=0.0):
        node = self.add("ShaderNodeMath", operation=operation)
        for index, value in enumerate((a, b)):
            if isinstance(value, (int, float)):
                node.inputs[index].default_value = value
            else:
                self.links.new(value, node.inputs[index])
        return node.outputs[0]

    def scaled(self, vector, factor):
        node = self.add("ShaderNodeVectorMath", operation="SCALE")
        self.links.new(vector, node.inputs[0])
        node.inputs["Scale"].default_value = factor
        return node.outputs["Vector"]

    def ridged(self, vector, scale, width):
        return self.remap(self.math("ABSOLUTE", self.math("SUBTRACT", self.noise(vector, scale, 2.0), 0.5)),
                          (0.0, width), (1.0, 0.0))

    def mix(self, factor, a, b):
        node = self.add("ShaderNodeMix", data_type="RGBA")
        self.link(factor, node, "Factor_Float")
        for socket, value in (("A_Color", a), ("B_Color", b)):
            if isinstance(value, tuple):
                next(s for s in node.inputs if s.identifier == socket).default_value = (*value, 1.0)
            else:
                self.link(value, node, socket)
        return node.outputs["Result"]


def belly(tree):
    split = tree.add("ShaderNodeSeparateXYZ")
    tree.link(tree.add("ShaderNodeNewGeometry").outputs["Normal"], split, "Vector")
    return tree.remap(split.outputs["Z"], (-0.7, 0.1), (1.0, 0.0))


def hide(tree, vector):
    edge = tree.voronoi(vector, 1.0, "DISTANCE_TO_EDGE")
    small = tree.remap(tree.voronoi(vector, 3.1, "DISTANCE_TO_EDGE"), (0.0, 0.06), (0.5, 0.0))
    crevice = tree.math("MAXIMUM", tree.remap(edge, (0.0, 0.09), (1.0, 0.0)), small)
    height = tree.math("SUBTRACT", tree.remap(edge, (0.0, 0.35)), tree.math("MULTIPLY", crevice, 0.3))
    return crevice, height, belly(tree)


def plate(tree, vector):
    edge = tree.voronoi(vector, 1.0, "DISTANCE_TO_EDGE")
    dome = tree.remap(tree.voronoi(vector, 1.0), (0.0, 0.7), (1.0, 0.0))
    scratch = tree.remap(tree.noise(tree.scaled(vector, 6.0), 4.0, 2.0), (0.62, 0.7))
    raised = tree.math("MULTIPLY", dome, tree.remap(edge, (0.0, 0.12)))
    height = tree.math("SUBTRACT", raised, tree.math("MULTIPLY", scratch, 0.15))
    return tree.remap(edge, (0.0, 0.07), (1.0, 0.0)), height, tree.remap(edge, (0.05, 0.12), (1.0, 0.0))


def membrane(tree, vector):
    warp = tree.add("ShaderNodeVectorMath", operation="MULTIPLY_ADD")
    tree.links.new(tree.noise(vector, 1.5, 3.0).node.outputs["Color"], warp.inputs[0])
    warp.inputs[1].default_value = (0.3,) * 3
    tree.links.new(vector, warp.inputs[2])
    warped = warp.outputs["Vector"]
    lines = tree.math("MAXIMUM", tree.ridged(warped, 0.9, 0.012),
                      tree.math("MULTIPLY", tree.ridged(warped, 3.5, 0.01), 0.5))
    wrinkle = tree.math("MULTIPLY", tree.noise(tree.scaled(vector, 3.0), 6.0, 4.0), 0.25)
    return lines, tree.math("ADD", lines, wrinkle), tree.noise(vector, 0.6, 2.0)


def keratin(tree, vector):
    along = tree.add("ShaderNodeAttribute", attribute_name="along").outputs["Fac"]
    wobble = tree.math("MULTIPLY", tree.noise(vector, 2.0, 3.0), 0.8)
    ridge = tree.remap(tree.math("SINE", tree.math("ADD", tree.math("MULTIPLY", along, 70.0), wobble)), (-1.0, 1.0))
    grooves = tree.math("MULTIPLY", tree.noise(tree.scaled(vector, 4.0), 3.0, 6.0), 0.3)
    height = tree.math("ADD", tree.math("MULTIPLY", ridge, 0.7), grooves)
    return tree.math("MULTIPLY", tree.remap(ridge, (0.0, 0.4), (1.0, 0.0)), 0.6), height, along


PATTERNS = {"hide": hide, "plate": plate, "membrane": membrane, "keratin": keratin}


def material(name, kind, cell=0.06, colors=None):
    if kind not in PATTERNS:
        raise ValueError(f"kind must be one of {sorted(PATTERNS)}, got {kind}")
    dark, mid, light = colors or PALETTES[kind]
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    tree = Tree(mat)
    mapping = tree.add("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (1 / cell,) * 3
    tree.link(tree.add("ShaderNodeTexCoord").outputs["Object"], mapping, "Vector")
    vector = mapping.outputs["Vector"]
    crevice, height, zone = PATTERNS[kind](tree, vector)
    shade = tree.mix(tree.remap(tree.noise(vector, 0.15, 6.0), (0.3, 0.7)), mid, tuple(c * 0.75 for c in mid))
    shader = tree.add("ShaderNodeBsdfPrincipled")
    tree.link(tree.mix(crevice, tree.mix(zone, shade, light), dark), shader, "Base Color")
    tree.link(tree.remap(crevice, (0.0, 1.0), (0.3 if kind == "keratin" else 0.45, 0.85)), shader, "Roughness")
    bump = tree.add("ShaderNodeBump", Strength=0.4 if kind == "membrane" else 0.8, Distance=cell * 0.15)
    tree.link(height, bump, "Height")
    tree.link(bump.outputs["Normal"], shader, "Normal")
    if kind == "membrane":
        shader.inputs["Subsurface Weight"].default_value = 0.35
        shader.inputs["Subsurface Radius"].default_value = (0.4, 0.08, 0.05)
    tree.link(shader.outputs["BSDF"], tree.add("ShaderNodeOutputMaterial"), "Surface")
    return mat
