# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Change Author:__Skii____________/
# __Created:________16.12.2015______/
# __Last_modified:__10.03.2026______/
# __Version:_0.3_Sub1(Community_Fix)/
# __________________________________/

"""
This file generates and modifies a ring-shaped mesh.
"""

import bpy
from bpy.props import FloatProperty, IntProperty, BoolProperty, PointerProperty
from mathutils import Quaternion, Vector
from .gen_func import bridgeLoops, create_mesh_object
from math import pi


WRing_Defaults = {
    "radius_out": 1.0,
    "use_inner": True,
    "radius_in": 0.0,
    "seg_perimeter": 24,
    "seg_radius": 1,
    "sector_from": 0.0,
    "sector_to": 2 * pi
}


def primitive_Ring(
        radius_out=1.0,
        use_inner=True,
        radius_in=0.0,
        seg_perimeter=24,
        seg_radius=1,
        sector_from=0.0,
        sector_to=2 * pi):

    verts = []
    edges = []
    faces = []
    loops = []

    if radius_out < radius_in:
        radius_in, radius_out = radius_out, radius_in

    if sector_from > sector_to:
        sector_to, sector_from = sector_from, sector_to

    if (radius_out - radius_in) < 0.0001:
        use_inner = False

    if seg_perimeter < 3:
        seg_perimeter = 3

    stepAngle = (sector_to - sector_from) / seg_perimeter
    stepRadius = (radius_out - radius_in) / seg_radius

    loop_number = seg_radius
    if radius_in > 0.0001:
        loop_number = seg_radius + 1

    seg_number = seg_perimeter
    closed = True
    if sector_to - sector_from < (2 * pi):
        seg_number = seg_perimeter + 1
        closed = False

    if use_inner:

        for r in range(loop_number):
            loop = []
            for s in range(seg_number):
                loop.append(len(verts))
                quat = Quaternion((0, 0, 1), (s * stepAngle) + sector_from)
                verts.append(quat @ Vector((radius_out - (r * stepRadius), 0.0, 0.0)))
            loops.append(loop)

        for i in range(len(loops) - 1):
            faces.extend(bridgeLoops(loops[i], loops[i + 1], closed))

        if loop_number == seg_radius:
            verts.append(Vector((0.0, 0.0, 0.0)))
            for s in range(seg_number - 1):
                faces.append((loops[-1][s], loops[-1][s + 1], len(verts) - 1))
            if seg_number == seg_perimeter:
                faces.append((loops[-1][-1], loops[-1][0], len(verts) - 1))

    else:

        for s in range(seg_number):
            quat = Quaternion((0, 0, 1), (s * stepAngle) + sector_from)
            verts.append(quat @ Vector((radius_out, 0.0, 0.0)))

        for v in range(len(verts) - 1):
            edges.append((v, v + 1))

        if closed:
            edges.append((len(verts) - 1, 0))

    return verts, edges, faces


def update_ring(self, context):

    if context.object is None:
        return

    mesh = context.object.data

    verts, edges, faces = primitive_Ring(
        self.radius_out,
        self.use_inner,
        self.radius_in,
        self.seg_perimeter,
        self.seg_radius,
        self.sector_from,
        self.sector_to
    )

    mesh.clear_geometry()
    mesh.from_pydata(verts, edges, faces)
    mesh.update()


class WRingData(bpy.types.PropertyGroup):

    radius_out: FloatProperty(
        name="Outer",
        default=1.0,
        min=0.0,
        update=update_ring
    )

    use_inner: BoolProperty(
        name="Use Inner",
        default=True,
        update=update_ring
    )

    radius_in: FloatProperty(
        name="Inner",
        default=0.0,
        min=0.0,
        update=update_ring
    )

    seg_perimeter: IntProperty(
        name="Perimeter",
        default=24,
        min=3,
        update=update_ring
    )

    seg_radius: IntProperty(
        name="Radius",
        default=1,
        min=1,
        update=update_ring
    )

    sector_from: FloatProperty(
        name="From",
        default=0.0,
        min=0.0,
        max=2 * pi,
        unit='ROTATION',
        update=update_ring
    )

    sector_to: FloatProperty(
        name="To",
        default=2 * pi,
        min=0.0,
        max=2 * pi,
        unit='ROTATION',
        update=update_ring
    )


class Make_WRing(bpy.types.Operator):
    """Create primitive WRing"""
    bl_idname = "mesh.make_wring"
    bl_label = "WRing"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):

        verts, edges, faces = primitive_Ring(**WRing_Defaults)

        obj = create_mesh_object(context, verts, edges, faces, "WRing")
        mesh = obj.data

        mesh.WType = 'WRING'

        mesh.WRing.radius_out = WRing_Defaults["radius_out"]
        mesh.WRing.radius_in = WRing_Defaults["radius_in"]
        mesh.WRing.use_inner = WRing_Defaults["use_inner"]
        mesh.WRing.seg_perimeter = WRing_Defaults["seg_perimeter"]
        mesh.WRing.seg_radius = WRing_Defaults["seg_radius"]
        mesh.WRing.sector_from = WRing_Defaults["sector_from"]
        mesh.WRing.sector_to = WRing_Defaults["sector_to"]

        return {'FINISHED'}


def drawWRingPanel(self, context):

    layout = self.layout
    data = context.object.data.WRing

    layout.label(text="Type: WRing", icon='MESH_CIRCLE')

    row = layout.row()

    col = row.column(align=True)
    col.label(text="Radiuses")
    col.prop(data, "radius_out")
    col.prop(data, "radius_in")

    col = row.column(align=True)
    col.label(text="Segmentation")
    col.prop(data, "seg_perimeter")
    col.prop(data, "seg_radius")

    col = row.column(align=True)
    col.label(text="Section")
    col.prop(data, "sector_from")
    col.prop(data, "sector_to")

    layout.prop(data, "use_inner")


def registerWRing():
    bpy.utils.register_class(Make_WRing)
    bpy.utils.register_class(WRingData)
    bpy.types.Mesh.WRing = PointerProperty(type=WRingData)


def unregisterWRing():
    bpy.utils.unregister_class(Make_WRing)
    bpy.utils.unregister_class(WRingData)
    del bpy.types.Mesh.WRing
