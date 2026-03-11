# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Change Author:__Skii____________/
# __Created:________03.04.2018______/
# __Last_modified:__10.03.2026______/
# __Version:_0.1_Sub1(Community_Fix)/
# __________________________________/

import bpy
from mathutils import Vector, Quaternion
from math import pi as PI
from bpy.props import BoolProperty, IntProperty, FloatProperty, PointerProperty

from .gen_func import (
    circleVerts as circ_V,
    moveVerts as move_V,
    fanClose,
    bridgeLoops,
    create_mesh_object as c_mesh
)


WCapsule_Defaults = {
    "radius": 0.5,
    "height": 2.0,
    "seg_perimeter": 24,
    "seg_height": 1,
    "seg_caps": 8,
    "centered": True,
    "smoothed": True
}


def primitive_Capsule_ME(
        radius=0.5,
        height=2.0,
        seg_perimeter=24,
        seg_height=1,
        seg_caps=8,
        centered=True,
        smoothed=True):

    verts = []
    edges = []
    faces = []
    loops = []

    if seg_perimeter < 3:
        seg_perimeter = 3

    if seg_height < 1:
        seg_height = 1

    if seg_caps < 1:
        seg_caps = 1

    if radius > height / 2:
        radius = height / 2

    verts.append(Vector((0, 0, 0)))
    verts.append(Vector((0, 0, height)))

    if seg_caps > 1:
        angleStep = PI / (2 * seg_caps)

        for i in range(1, seg_caps):

            quat = Quaternion((0, -1, 0), i * angleStep)
            helperVect = quat @ Vector((0, 0, -radius))

            segmentRadius = helperVect.x
            segmentHeight = radius + helperVect.z

            newVerts, loop = circ_V(segmentRadius, seg_perimeter, len(verts))
            move_V(newVerts, Vector((0, 0, segmentHeight)))

            verts.extend(newVerts)
            loops.append(loop)

    newVerts, loop = circ_V(radius, seg_perimeter, len(verts))
    move_V(newVerts, Vector((0, 0, radius)))

    verts.extend(newVerts)
    loops.append(loop)

    if height > 2 * radius:

        if seg_height > 1:

            heightStep = (height - (2 * radius)) / seg_height

            for i in range(1, seg_height):

                newHeight = (i * heightStep) + radius

                newVerts, loop = circ_V(radius, seg_perimeter, len(verts))
                move_V(newVerts, Vector((0, 0, newHeight)))

                verts.extend(newVerts)
                loops.append(loop)

        newVerts, loop = circ_V(radius, seg_perimeter, len(verts))
        move_V(newVerts, Vector((0, 0, height - radius)))

        verts.extend(newVerts)
        loops.append(loop)

    if seg_caps > 1:

        angleStep = PI / (2 * seg_caps)

        for i in range(1, seg_caps):

            quat = Quaternion((0, -1, 0), i * angleStep)
            helperVect = quat @ Vector((radius, 0, 0))

            segmentRadius = helperVect.x
            segmentHeight = height - radius + helperVect.z

            newVerts, loop = circ_V(segmentRadius, seg_perimeter, len(verts))
            move_V(newVerts, Vector((0, 0, segmentHeight)))

            verts.extend(newVerts)
            loops.append(loop)

    faces.extend(fanClose(loops[0], 0, flipped=True))
    faces.extend(fanClose(loops[-1], 1))

    for i in range(1, len(loops)):
        faces.extend(bridgeLoops(loops[i - 1], loops[i], True))

    if centered:
        move_V(verts, Vector((0, 0, -height / 2)))

    return verts, edges, faces


def update_capsule(self, context):

    if context.object is None:
        return

    mesh = context.object.data

    verts, edges, faces = primitive_Capsule_ME(
        self.radius,
        self.height,
        self.seg_perimeter,
        self.seg_height,
        self.seg_caps,
        self.centered,
        self.smoothed
    )

    mesh.clear_geometry()
    mesh.from_pydata(verts, edges, faces)
    mesh.update()

    for poly in mesh.polygons:
        poly.use_smooth = self.smoothed


class WCapsuleData(bpy.types.PropertyGroup):

    radius: FloatProperty(
        name="Radius",
        default=0.5,
        min=0.0,
        update=update_capsule
    )

    height: FloatProperty(
        name="Height",
        default=2.0,
        min=0.0,
        update=update_capsule
    )

    seg_perimeter: IntProperty(
        name="Perimeter",
        default=24,
        min=3,
        update=update_capsule
    )

    seg_height: IntProperty(
        name="Height Segments",
        default=1,
        min=1,
        update=update_capsule
    )

    seg_caps: IntProperty(
        name="Caps Segments",
        default=6,
        min=1,
        update=update_capsule
    )

    centered: BoolProperty(
        name="Centered",
        default=False,
        update=update_capsule
    )

    smoothed: BoolProperty(
        name="Smooth",
        default=True,
        update=update_capsule
    )


class Make_WCapsule(bpy.types.Operator):

    bl_idname = "mesh.make_wcapsule"
    bl_label = "WCapsule"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):

        verts, edges, faces = primitive_Capsule_ME(**WCapsule_Defaults)

        obj = c_mesh(context, verts, edges, faces, "WCapsule")
        mesh = obj.data

        mesh.WType = 'WCAPSULE'

        mesh.WCapsule.radius = WCapsule_Defaults["radius"]
        mesh.WCapsule.height = WCapsule_Defaults["height"]
        mesh.WCapsule.seg_perimeter = WCapsule_Defaults["seg_perimeter"]
        mesh.WCapsule.seg_height = WCapsule_Defaults["seg_height"]
        mesh.WCapsule.seg_caps = WCapsule_Defaults["seg_caps"]
        mesh.WCapsule.centered = WCapsule_Defaults["centered"]
        mesh.WCapsule.smoothed = WCapsule_Defaults["smoothed"]

        return {'FINISHED'}


def drawWCapsulePanel(self, context):

    layout = self.layout
    data = context.object.data.WCapsule

    layout.label(text="Type: WCapsule", icon="MESH_CAPSULE")

    row = layout.row()

    col = row.column(align=True)
    col.prop(data, "radius")
    col.prop(data, "height")

    col = row.column(align=True)
    col.prop(data, "seg_perimeter")
    col.prop(data, "seg_height")
    col.prop(data, "seg_caps")

    row = layout.row(align=True)
    row.prop(data, "centered")
    row.prop(data, "smoothed")


def registerWCapsule():
    bpy.utils.register_class(Make_WCapsule)
    bpy.utils.register_class(WCapsuleData)
    bpy.types.Mesh.WCapsule = PointerProperty(type=WCapsuleData)


def unregisterWCapsule():
    bpy.utils.unregister_class(Make_WCapsule)
    bpy.utils.unregister_class(WCapsuleData)
    del bpy.types.Mesh.WCapsule
