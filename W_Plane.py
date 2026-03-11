# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Change Author:__Skii____________/
# __Created:________15.12.2015______/
# __Last_modified:__10.03.2026______/
# __Version:_0.3_Sub1(Community_Fix)/
# __________________________________/

import bpy
import bmesh
from bpy.props import FloatProperty, IntProperty, BoolProperty, PointerProperty
from mathutils import Vector
from .gen_func import bridgeLoops, create_mesh_object


WPlane_Defaults = {
    "size_x": 2.0,
    "size_y": 2.0,
    "seg_x": 1,
    "seg_y": 1,
    "centered": True
}


def WPlane_mesh(size_x=2.0, size_y=2.0, seg_x=1, seg_y=1, centered=True):

    verts = []
    edges = []
    faces = []
    lines = []

    dist_x = size_x / seg_x
    dist_y = size_y / seg_y

    for i in range(seg_y + 1):
        line = []
        for j in range(seg_x + 1):
            line.append(len(verts))
            verts.append(Vector((j * dist_x, i * dist_y, 0.0)))
        lines.append(line)

    for i in range(len(lines) - 1):
        faces.extend(bridgeLoops(lines[i], lines[i + 1], False))

    if centered:
        half_x = size_x / 2
        half_y = size_y / 2
        for v in verts:
            v[0] -= half_x
            v[1] -= half_y

    return verts, edges, faces


def update_plane(self, context):

    if context.object is None:
        return

    mesh = context.object.data

    verts, edges, faces = WPlane_mesh(
        self.size_x,
        self.size_y,
        self.seg_x,
        self.seg_y,
        self.centered
    )

    mesh.clear_geometry()
    mesh.from_pydata(verts, edges, faces)
    mesh.update()


class WPlaneData(bpy.types.PropertyGroup):

    size_x: FloatProperty(
        name="X",
        default=2.0,
        min=0.0,
        update=update_plane
    )

    size_y: FloatProperty(
        name="Y",
        default=2.0,
        min=0.0,
        update=update_plane
    )

    seg_x: IntProperty(
        name="X",
        default=1,
        min=1,
        update=update_plane
    )

    seg_y: IntProperty(
        name="Y",
        default=1,
        min=1,
        update=update_plane
    )

    centered: BoolProperty(
        name="Centered",
        default=True,
        update=update_plane
    )


class Make_WPlane(bpy.types.Operator):
    """Create primitive WPlane"""
    bl_idname = "mesh.make_wplane"
    bl_label = "WPlane"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):

        verts, edges, faces = WPlane_mesh(**WPlane_Defaults)

        obj = create_mesh_object(context, verts, edges, faces, "WPlane")
        mesh = obj.data

        mesh.WType = 'WPLANE'

        mesh.WPlane.size_x = WPlane_Defaults["size_x"]
        mesh.WPlane.size_y = WPlane_Defaults["size_y"]
        mesh.WPlane.seg_x = WPlane_Defaults["seg_x"]
        mesh.WPlane.seg_y = WPlane_Defaults["seg_y"]
        mesh.WPlane.centered = WPlane_Defaults["centered"]

        mesh.WPlane["thisMesh"] = mesh.name

        return {'FINISHED'}


def drawWPlanePanel(self, context):

    layout = self.layout
    data = context.object.data.WPlane

    layout.label(text="Type: WPlane", icon='MESH_PLANE')

    row = layout.row()

    col = row.column(align=True)
    col.label(text="Size")
    col.prop(data, "size_x")
    col.prop(data, "size_y")

    col = row.column(align=True)
    col.label(text="Segments")
    col.prop(data, "seg_x")
    col.prop(data, "seg_y")

    layout.prop(data, "centered")


def registerWPlane():
    bpy.utils.register_class(Make_WPlane)
    bpy.utils.register_class(WPlaneData)
    bpy.types.Mesh.WPlane = PointerProperty(type=WPlaneData)


def unregisterWPlane():
    bpy.utils.unregister_class(Make_WPlane)
    bpy.utils.unregister_class(WPlaneData)
    del bpy.types.Mesh.WPlane
