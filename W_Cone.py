# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Change Author:__Skii____________/
# __Created:________16.12.2015______/
# __Last_modified:__10.03.2026______/
# __Version:_0.2_Sub1(Community_Fix)/
# __________________________________/

import bpy
from mathutils import Vector
from bpy.props import BoolProperty, IntProperty, FloatProperty, PointerProperty

from .gen_func import (
    circleVerts as circ_V,
    moveVerts as move_V,
    fanClose,
    bridgeLoops,
    create_mesh_object as c_mesh
)


WCone_Defaults = {
    "radius_main": 1.0,
    "radius_top": 0.0,
    "height": 2.0,
    "seg_perimeter": 24,
    "seg_height": 1,
    "seg_radius": 1,
    "centered": False,
    "smoothed": True
}


def primitive_Cone_ME(
        radius_main=1.0,
        radius_top=0.0,
        height=2.0,
        seg_perimeter=24,
        seg_height=1,
        seg_radius=1,
        centered=False,
        smoothed=True):

    verts = []
    edges = []
    faces = []

    loops = []

    if seg_perimeter < 3:
        seg_perimeter = 3
    if seg_height < 1:
        seg_height = 1
    if seg_radius < 1:
        seg_radius = 1

    verts.append(Vector((0, 0, 0)))
    verts.append(Vector((0, 0, height)))

    if radius_top == 0 and radius_main == 0:
        edges.append((0, 1))
        return verts, edges, faces

    if radius_main > 0:
        if seg_radius > 1:
            step = radius_main / seg_radius
            for i in range(1, seg_radius):
                newVerts, loop = circ_V(i * step, seg_perimeter, len(verts))
                verts.extend(newVerts)
                loops.append(loop)

        newVerts, loop = circ_V(radius_main, seg_perimeter, len(verts))
        verts.extend(newVerts)
        loops.append(loop)

    if seg_height > 1:
        heightStep = height / seg_height
        radiusStep = (radius_top - radius_main) / seg_height
        for i in range(1, seg_height):
            newRadius = radius_main + (i * radiusStep)
            newVerts, loop = circ_V(newRadius, seg_perimeter, len(verts))
            move_V(newVerts, Vector((0, 0, heightStep * i)))
            verts.extend(newVerts)
            loops.append(loop)

    if radius_top > 0:
        newVerts, loop = circ_V(radius_top, seg_perimeter, len(verts))
        move_V(newVerts, Vector((0, 0, height)))
        verts.extend(newVerts)
        loops.append(loop)

        if seg_radius > 1:
            step = radius_top / seg_radius
            for i in range(1, seg_radius):
                newRadius = radius_top - (i * step)
                newVerts, loop = circ_V(newRadius, seg_perimeter, len(verts))
                move_V(newVerts, Vector((0, 0, height)))
                verts.extend(newVerts)
                loops.append(loop)

    faces.extend(fanClose(loops[0], 0, closed=True, flipped=True))
    faces.extend(fanClose(loops[-1], 1))

    for i in range(1, len(loops)):
        faces.extend(bridgeLoops(loops[i - 1], loops[i], True))

    if centered:
        move_V(verts, Vector((0, 0, -height / 2)))

    return verts, edges, faces


def update_cone(self, context):

    if context.object is None:
        return

    mesh = context.object.data

    verts, edges, faces = primitive_Cone_ME(
        self.rad_main,
        self.rad_top,
        self.height,
        self.seg_perimeter,
        self.seg_height,
        self.seg_radius,
        self.centered,
        self.smoothed
    )

    mesh.clear_geometry()
    mesh.from_pydata(verts, edges, faces)

    if self.smoothed:
        for poly in mesh.polygons:
            poly.use_smooth = True

    mesh.update()


class WConeData(bpy.types.PropertyGroup):

    rad_top: FloatProperty(
        name="Radius top",
        default=0.0,
        min=0.0,
        update=update_cone
    )

    rad_main: FloatProperty(
        name="Radius bottom",
        default=1.0,
        min=0.0,
        update=update_cone
    )

    height: FloatProperty(
        name="Height",
        default=2.0,
        min=0.0,
        update=update_cone
    )

    seg_perimeter: IntProperty(
        name="Perim Segments",
        default=24,
        min=3,
        update=update_cone
    )

    seg_height: IntProperty(
        name="Height Segments",
        default=1,
        min=1,
        update=update_cone
    )

    seg_radius: IntProperty(
        name="Radius Segments",
        default=1,
        min=1,
        update=update_cone
    )

    centered: BoolProperty(
        name="Centered",
        default=False,
        update=update_cone
    )

    smoothed: BoolProperty(
        name="Smooth",
        default=True,
        update=update_cone
    )


class Make_WCone(bpy.types.Operator):
    """Create primitive WCone mesh"""
    bl_idname = "mesh.make_wcone"
    bl_label = "WCone"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):

        verts, edges, faces = primitive_Cone_ME(**WCone_Defaults)

        obj = c_mesh(context, verts, edges, faces, "WCone")
        mesh = obj.data

        mesh.WType = 'WCONE'

        mesh.WCone.rad_top = WCone_Defaults["radius_top"]
        mesh.WCone.rad_main = WCone_Defaults["radius_main"]
        mesh.WCone.height = WCone_Defaults["height"]
        mesh.WCone.seg_perimeter = WCone_Defaults["seg_perimeter"]
        mesh.WCone.seg_height = WCone_Defaults["seg_height"]
        mesh.WCone.seg_radius = WCone_Defaults["seg_radius"]
        mesh.WCone.centered = WCone_Defaults["centered"]
        mesh.WCone.smoothed = WCone_Defaults["smoothed"]

        bpy.ops.object.shade_smooth()

        return {'FINISHED'}


def drawWConePanel(self, context):

    layout = self.layout
    data = context.object.data.WCone

    layout.label(text="Type: WCone", icon="MESH_CONE")

    row = layout.row()

    col = row.column(align=True)
    col.prop(data, "rad_top")
    col.prop(data, "rad_main")
    col.prop(data, "height")

    col = row.column(align=True)
    col.prop(data, "seg_perimeter")
    col.prop(data, "seg_height")
    col.prop(data, "seg_radius")

    row = layout.row()
    row.prop(data, "centered")
    row.prop(data, "smoothed")


def registerWCone():
    bpy.utils.register_class(Make_WCone)
    bpy.utils.register_class(WConeData)
    bpy.types.Mesh.WCone = PointerProperty(type=WConeData)


def unregisterWCone():
    bpy.utils.unregister_class(Make_WCone)
    bpy.utils.unregister_class(WConeData)
    del bpy.types.Mesh.WCone
