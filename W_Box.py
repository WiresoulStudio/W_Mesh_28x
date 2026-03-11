# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Change Author:__Skii/
# __Created:________15.12.2015______/
# __Last_modified:__10.03.2026______/
# __Version:_0.3_Sub1(Community_Fix)/
# __________________________________/

"""
Modernized WBox primitive for Blender 5
"""

import bpy
from bpy.props import FloatProperty, IntProperty, BoolProperty, PointerProperty
from mathutils import Vector
from .gen_func import bridgeLoops, create_mesh_object


WBox_Defaults = {
    "size_x": 2.0,
    "size_y": 2.0,
    "size_z": 2.0,
    "seg_x": 1,
    "seg_y": 1,
    "seg_z": 1,
    "centered": True
}


def primitive_Box(
        size_x=2.0,
        size_y=2.0,
        size_z=2.0,
        seg_x=1,
        seg_y=1,
        seg_z=1,
        centered=True):

    verts = []
    edges = []
    faces = []

    bottom_lines = []
    top_lines = []
    loops = []

    dist_x = size_x / seg_x
    dist_y = size_y / seg_y
    dist_z = size_z / seg_z

    # bottom grid
    for y in range(seg_y + 1):
        line = []
        for x in range(seg_x + 1):
            line.append(len(verts))
            verts.append(Vector((x * dist_x, y * dist_y, 0.0)))
        bottom_lines.append(line)

    # top grid
    for y in range(seg_y + 1):
        line = []
        for x in range(seg_x + 1):
            line.append(len(verts))
            verts.append(Vector((x * dist_x, y * dist_y, size_z)))
        top_lines.append(line)

    # bottom loop
    loop = []
    for i in range(seg_x + 1):
        loop.append(bottom_lines[0][i])
    for i in range(seg_y - 1):
        loop.append(bottom_lines[i + 1][-1])
    for i in range(seg_x + 1):
        loop.append(bottom_lines[-1][-(i + 1)])
    for i in range(seg_y - 1):
        loop.append(bottom_lines[-(i + 2)][0])
    loops.append(loop)

    # z loops
    for z in range(seg_z - 1):
        loop = []
        for i in range(seg_x + 1):
            loop.append(len(verts))
            verts.append(Vector((i * dist_x, 0.0, (z + 1) * dist_z)))
        for i in range(seg_y - 1):
            loop.append(len(verts))
            verts.append(Vector((size_x, (i + 1) * dist_y, (z + 1) * dist_z)))
        for i in range(seg_x + 1):
            loop.append(len(verts))
            verts.append(Vector((size_x - (i * dist_x), size_y, (z + 1) * dist_z)))
        for i in range(seg_y - 1):
            loop.append(len(verts))
            verts.append(Vector((0.0, size_y - ((i + 1) * dist_y), (z + 1) * dist_z)))
        loops.append(loop)

    # top loop
    loop = []
    for i in range(seg_x + 1):
        loop.append(top_lines[0][i])
    for i in range(seg_y - 1):
        loop.append(top_lines[i + 1][-1])
    for i in range(seg_x + 1):
        loop.append(top_lines[-1][-(i + 1)])
    for i in range(seg_y - 1):
        loop.append(top_lines[-(i + 2)][0])
    loops.append(loop)

    # bottom faces
    for i in range(seg_y):
        faces.extend(bridgeLoops(bottom_lines[i], bottom_lines[i + 1], False))

    # top faces
    for i in range(seg_y):
        faces.extend(bridgeLoops(top_lines[i], top_lines[i + 1], False))

    # side faces
    for i in range(seg_z):
        faces.extend(bridgeLoops(loops[i], loops[i + 1], True))

    if centered:
        half_x = size_x / 2
        half_y = size_y / 2
        half_z = size_z / 2
        for v in verts:
            v -= Vector((half_x, half_y, half_z))

    return verts, edges, faces


def update_box(self, context):

    if context.object is None:
        return

    mesh = context.object.data

    verts, edges, faces = primitive_Box(
        self.size_x,
        self.size_y,
        self.size_z,
        self.seg_x,
        self.seg_y,
        self.seg_z,
        self.centered
    )

    mesh.clear_geometry()
    mesh.from_pydata(verts, edges, faces)
    mesh.update()


class WBoxData(bpy.types.PropertyGroup):

    size_x: FloatProperty(name="X", default=2.0, min=0.0, update=update_box)
    size_y: FloatProperty(name="Y", default=2.0, min=0.0, update=update_box)
    size_z: FloatProperty(name="Z", default=2.0, min=0.0, update=update_box)

    seg_x: IntProperty(name="X", default=1, min=1, update=update_box)
    seg_y: IntProperty(name="Y", default=1, min=1, update=update_box)
    seg_z: IntProperty(name="Z", default=1, min=1, update=update_box)

    centered: BoolProperty(name="Centered", default=True, update=update_box)


class Make_WBox(bpy.types.Operator):
    """Create primitive WBox"""
    bl_idname = "mesh.make_wbox"
    bl_label = "WBox"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):

        verts, edges, faces = primitive_Box(**WBox_Defaults)

        obj = create_mesh_object(context, verts, edges, faces, "WBox")
        mesh = obj.data

        mesh.WType = 'WBOX'

        mesh.WBox.size_x = WBox_Defaults["size_x"]
        mesh.WBox.size_y = WBox_Defaults["size_y"]
        mesh.WBox.size_z = WBox_Defaults["size_z"]
        mesh.WBox.seg_x = WBox_Defaults["seg_x"]
        mesh.WBox.seg_y = WBox_Defaults["seg_y"]
        mesh.WBox.seg_z = WBox_Defaults["seg_z"]
        mesh.WBox.centered = WBox_Defaults["centered"]

        return {'FINISHED'}


def drawWBoxPanel(self, context):

    layout = self.layout
    data = context.object.data.WBox

    layout.label(text="Type: WBox", icon='MESH_CUBE')

    row = layout.row()

    col = row.column(align=True)
    col.label(text="Size")
    col.prop(data, "size_x")
    col.prop(data, "size_y")
    col.prop(data, "size_z")

    col = row.column(align=True)
    col.label(text="Segments")
    col.prop(data, "seg_x")
    col.prop(data, "seg_y")
    col.prop(data, "seg_z")

    layout.prop(data, "centered")


def registerWBox():
    bpy.utils.register_class(Make_WBox)
    bpy.utils.register_class(WBoxData)
    bpy.types.Mesh.WBox = PointerProperty(type=WBoxData)


def unregisterWBox():
    bpy.utils.unregister_class(Make_WBox)
    bpy.utils.unregister_class(WBoxData)
    del bpy.types.Mesh.WBox
