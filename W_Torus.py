# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Change Author:__Skii____________/
# __Created:________03.04.2018______/
# __Last_modified:__11.03.2026______/
# __Version:_0.1_Sub1(Community_Fix)/
# __________________________________/

import bpy
from mathutils import Vector, Quaternion
from math import pi as PI
from bpy.props import BoolProperty, IntProperty, FloatProperty, PointerProperty
from .gen_func import (
    circleVerts as circ_V,
    moveVerts as move_V,
    rotateVerts as rot_V,
    fanClose,
    bridgeLoops,
    create_mesh_object as c_mesh
)


WTorus_Defaults = {
    "radius_main": 2.0,
    "radius_minor": 0.5,
    "seg_main": 24,
    "seg_minor": 12,
    "sec_from": 0.0,
    "sec_to": 2 * PI,
    "smoothed": True
}


def primitive_Torus_ME(
    radius_main=2.0,
    radius_minor=0.5,
    seg_main=24,
    seg_minor=12,
    sec_from=0.0,
    sec_to=2 * PI,
    smoothed=True):

    verts = []
    edges = []
    faces = []
    loops = []

    if seg_main < 3:
        seg_main = 3
    if seg_minor < 3:
        seg_minor = 3

    if sec_from > sec_to:
        sec_from, sec_to = sec_to, sec_from

    seg_angle = (sec_to - sec_from) / seg_main
    quatRight = Quaternion((-1, 0, 0), PI / 2)
    vecOffset = Vector((radius_main, 0, 0))

    for i in range(seg_main):

        quat = Quaternion((0, 0, 1), (i * seg_angle) + sec_from)

        newVerts, loop = circ_V(radius_minor, seg_minor, len(verts))

        rot_V(newVerts, quatRight)
        move_V(newVerts, vecOffset)
        rot_V(newVerts, quat)

        verts.extend(newVerts)
        loops.append(loop)

    if sec_to - sec_from < 2 * PI:

        quat = Quaternion((0, 0, 1), sec_to)
        newVerts, loop = circ_V(radius_minor, seg_minor, len(verts))

        rot_V(newVerts, quatRight)
        move_V(newVerts, vecOffset)
        rot_V(newVerts, quat)

        verts.extend(newVerts)
        loops.append(loop)

        verts.append(quat @ vecOffset)
        quat = Quaternion((0, 0, 1), sec_from)
        verts.append(quat @ vecOffset)

        faces.extend(fanClose(loops[0], len(verts) - 1, flipped=True))
        faces.extend(fanClose(loops[-1], len(verts) - 2))

    else:
        faces.extend(bridgeLoops(loops[-1], loops[0], True))

    for i in range(1, len(loops)):
        faces.extend(bridgeLoops(loops[i - 1], loops[i], True))

    return verts, edges, faces


def update_torus(self, context):

    if context.object is None:
        return

    mesh = context.object.data

    verts, edges, faces = primitive_Torus_ME(
        self.radius_main,
        self.radius_minor,
        self.seg_main,
        self.seg_minor,
        self.sec_from,
        self.sec_to,
        self.smoothed
    )

    mesh.clear_geometry()
    mesh.from_pydata(verts, edges, faces)

    if self.smoothed:
        for p in mesh.polygons:
            p.use_smooth = True

    mesh.update()


class WTorusData(bpy.types.PropertyGroup):

    radius_main: FloatProperty(
        name="Major",
        default=2.0,
        min=0.0,
        update=update_torus
    )

    radius_minor: FloatProperty(
        name="Minor",
        default=0.5,
        min=0.0,
        update=update_torus
    )

    seg_main: IntProperty(
        name="Main",
        default=24,
        min=3,
        update=update_torus
    )

    seg_minor: IntProperty(
        name="Minor",
        default=12,
        min=3,
        update=update_torus
    )

    sec_from: FloatProperty(
        name="From",
        default=0.0,
        min=0.0,
        max=2 * PI,
        update=update_torus
    )

    sec_to: FloatProperty(
        name="To",
        default=2 * PI,
        min=0.0,
        max=2 * PI,
        update=update_torus
    )

    smoothed: BoolProperty(
        name="Smooth",
        default=True,
        update=update_torus
    )


class Make_WTorus(bpy.types.Operator):
    """Create primitive WTorus mesh"""
    bl_idname = "mesh.make_wtorus"
    bl_label = "WTorus"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):

        verts, edges, faces = primitive_Torus_ME(**WTorus_Defaults)

        obj = c_mesh(context, verts, edges, faces, "WTorus")
        mesh = obj.data

        mesh.WType = 'WTORUS'

        mesh.WTorus.radius_main = WTorus_Defaults["radius_main"]
        mesh.WTorus.radius_minor = WTorus_Defaults["radius_minor"]
        mesh.WTorus.seg_main = WTorus_Defaults["seg_main"]
        mesh.WTorus.seg_minor = WTorus_Defaults["seg_minor"]
        mesh.WTorus.sec_from = WTorus_Defaults["sec_from"]
        mesh.WTorus.sec_to = WTorus_Defaults["sec_to"]
        mesh.WTorus.smoothed = WTorus_Defaults["smoothed"]

        if mesh.WTorus.smoothed:
            for p in mesh.polygons:
                p.use_smooth = True

        return {'FINISHED'}


def drawWTorusPanel(self, context):

    layout = self.layout
    WData = context.object.data.WTorus

    layout.label(text="Type: WTorus", icon="MESH_TORUS")

    row = layout.row()

    col = row.column(align=True)
    col.label(text="Radiuses")
    col.prop(WData, "radius_main")
    col.prop(WData, "radius_minor")

    col = row.column(align=True)
    col.label(text="Segments")
    col.prop(WData, "seg_main")
    col.prop(WData, "seg_minor")

    layout.label(text="Section")
    layout.prop(WData, "sec_from")
    layout.prop(WData, "sec_to")

    layout.prop(WData, "smoothed")


def registerWTorus():
    bpy.utils.register_class(Make_WTorus)
    bpy.utils.register_class(WTorusData)
    bpy.types.Mesh.WTorus = PointerProperty(type=WTorusData)


def unregisterWTorus():
    bpy.utils.unregister_class(Make_WTorus)
    bpy.utils.unregister_class(WTorusData)
    del bpy.types.Mesh.WTorus
