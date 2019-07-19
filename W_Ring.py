# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Created:________16.07.2019______/
# __Version:________1.0_____________/
# __________________________________/

# imports
import bpy
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    PointerProperty
)
from bpy_extras import object_utils
from mathutils import Vector, Quaternion
from math import pi
from .genFunctions import (
    circleVerts as circ_V,
    moveVerts as move_V,
    fanClose,
    bridgeLoops,
    create_mesh_object
)

# generate geometry
def geoGen_WRing (
    radius_out,
    use_inner,
    radius_in,
    seg_perimeter,
    seg_radius,
    sector_from,
    sector_to):
    
    # Prepare empty lists
    verts = []
    edges = []
    faces = []

    loops = []

    # make sure of what is bigger
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
                verts.append(quat @ Vector((
                    radius_out - (r * stepRadius), 0.0, 0.0)))
            loops.append(loop)

        # fill the loops
        for i in range(len(loops) - 1):
            faces.extend(bridgeLoops(loops[i], loops[i + 1], closed))

        # one point in the middle
        if loop_number == seg_radius:
            verts.append(Vector((0.0, 0.0, 0.0)))
            for s in range(seg_number - 1):
                faces.append((loops[-1][s], loops[-1][s+1], len(verts) - 1))
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

def update_WRing (wData):
    return geoGen_WRing (
        radius_out = wData.rad_1,
        use_inner = wData.inn,
        radius_in = wData.rad_2,
        seg_perimeter = wData.seg_1,
        seg_radius = wData.seg_2,
        sector_from = wData.sec_f,
        sector_to = wData.sec_t
    )

# add object W_Plane
class Make_WRing(bpy.types.Operator):
    """Create primitive wRing"""
    bl_idname = "mesh.make_wring"
    bl_label = "wRing"
    bl_options = {'UNDO', 'REGISTER'}

    radius_out: FloatProperty(
        name="Outer",
        description="Outer radius",
        default=1.0,
        min=0.0,
        soft_min=0.0,
        step=1,
        unit='LENGTH'
    )

    use_inner: BoolProperty(
        name="Use inner",
        description="use inner radius",
        default=True
    )

    radius_in: FloatProperty(
        name="Inner",
        description="Inner radius",
        default=0.0,
        min=0.0,
        soft_min=0.0,
        step=1,
        unit='LENGTH'
    )

    seg_perimeter: IntProperty(
        name="Perimeter",
        description="Subdivision of the perimeter",
        default=24,
        min=3,
        soft_min=3,
        step=1
        )

    seg_radius: IntProperty(
        name="Radius",
        description="Subdivision of the radius",
        default=1,
        min=1,
        soft_min=1,
        step=1
        )

    sector_from: FloatProperty(
        name="From",
        description="Setor from",
        default=0.0,
        min=0.0,
        soft_min=0.0,
        max = 2 * pi,
        soft_max = 2 * pi,
        step=10,
        unit='ROTATION'
    )

    sector_to: FloatProperty(
        name="From",
        description="Setor from",
        default=2 * pi,
        min=0.0,
        soft_min=0.0,
        max = 2 * pi,
        soft_max = 2 * pi,
        step=10,
        unit='ROTATION'
    )

    def execute(self, context):

        mesh = bpy.data.meshes.new("wRing")

        wD = mesh.wData
        wD.rad_1 = self.radius_out
        wD.inn = self.use_inner
        wD.rad_2 = self.radius_in
        wD.seg_1 = self.seg_perimeter
        wD.seg_2 = self.seg_radius
        wD.sec_f = self.sector_from
        wD.sec_t = self.sector_to
        wD.wType = 'WRING'


        mesh.from_pydata(*update_WRing(wD))
        mesh.update()
        
        object_utils.object_data_add(context, mesh, operator=None)

        bpy.ops.object.shade_smooth()
        context.object.data.use_auto_smooth = True
        return {'FINISHED'}

# create UI panel
def draw_WRing_panel(self, context):
    lay_out = self.layout
    lay_out.use_property_split = True
    WData = context.object.data.wData

    lay_out.label(text="Type: wRing", icon='MESH_CIRCLE')

    col = lay_out.column(align=True)
    col.prop(WData, "rad_1", text="Radius Main")
    col.prop(WData, "rad_2", text="Inner")

    col = lay_out.column(align=True)
    col.prop(WData, "sec_f", text="Section From")
    col.prop(WData, "sec_t", text="To")
    
    col = lay_out.column(align=True)
    col.prop(WData, "seg_1", text="Segmentation Main")
    col.prop(WData, "seg_2", text="Cap")

    lay_out.prop(WData, "inn", text="Use inner radius")
    lay_out.prop(WData, "anim", text="Animated")


# register
def reg_wRing():
    bpy.utils.register_class(Make_WRing)
# unregister
def unreg_wRing():
    bpy.utils.unregister_class(Make_WRing)