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
def geoGen_WTube (
    radius_out,
    radius_in,
    height,
    use_inner,
    seg_perimeter,
    seg_radius,
    seg_height,
    sector_from,
    sector_to,
    centered,
    smoothed):
    
    # Prepare empty lists
    verts = []
    edges = []
    faces = []

    top_rings = []
    bottom_rings = []
    loops = []
    inner_loops = []
    midpoints = []

    # make sure of what is bigger
    if radius_out < radius_in:
        radius_in, radius_out = radius_out, radius_in

    if sector_from > sector_to:
        sector_to, sector_from = sector_from, sector_to

    if radius_out - radius_in < 0.0001:
        use_inner = False

    if seg_perimeter < 3:
        seg_perimeter = 3

    # sizes of chunks
    stepAngle = (sector_to - sector_from) / seg_perimeter
    stepRadius = (radius_out - radius_in) / seg_radius
    stepHeight = height / seg_height

    middlePoint = radius_in <= 0.0001
    closed = (sector_to - sector_from) >= 2 * pi
    seg_number = seg_perimeter
    if not closed:
        seg_number = seg_perimeter + 1
    rad_number = seg_radius
    if middlePoint:
        rad_number = seg_radius - 1

    # wall around
    for z in range(seg_height + 1):
        loop = []
        for s in range(seg_number):
            loop.append(len(verts))
            quat = Quaternion((0, 0, 1), (s * stepAngle) + sector_from)
            verts.append(quat @ Vector((radius_out, 0.0, z * stepHeight)))
        loops.append(loop)

    # fill the wall around
    for i in range(len(loops) - 1):
        faces.extend(bridgeLoops(loops[i], loops[i + 1], closed))

    if use_inner:
        # fill the caps (without the center)
        for z in range(2):
            if z == 0:
                bottom_rings.append(loops[0])
            else:
                top_rings.append(loops[-1])

            for r in range(rad_number):
                ring = []
                for s in range(seg_number):
                    ring.append(len(verts))
                    quat = Quaternion((0, 0, 1), (s * stepAngle) + sector_from)
                    verts.append(quat @ Vector((
                        radius_out - ((r + 1) * stepRadius),
                        0.0,
                        z * height)))
                if z == 0:
                    bottom_rings.append(ring)
                else:
                    top_rings.append(ring)

        for i in range(len(top_rings) - 1):
            faces.extend(bridgeLoops(top_rings[i], top_rings[i + 1], closed))
        for i in range(len(bottom_rings) - 1):
            faces.extend(bridgeLoops(
                bottom_rings[-(i + 1)], bottom_rings[-(i + 2)], closed))

        # fill the center
        if middlePoint:
            # fill with middle point
            if closed:
                for z in range(2):
                    midpoints.append(len(verts))
                    verts.append(Vector((0.0, 0.0, z * height)))
            else:
                for z in range(seg_height + 1):
                    midpoints.append(len(verts))
                    verts.append(Vector((0.0, 0.0, z * stepHeight)))

            # close the cup
            for s in range(seg_number - 1):
                faces.append((
                    bottom_rings[-1][s],
                    midpoints[0],
                    bottom_rings[-1][s + 1]))
                faces.append((
                    top_rings[-1][s], top_rings[-1][s + 1], midpoints[-1]))
            if closed:
                faces.append((
                    bottom_rings[-1][-1], midpoints[0], bottom_rings[-1][0]))
                faces.append((
                    top_rings[-1][-1], top_rings[-1][0], midpoints[-1]))

        else:
            # fill with inner loops
            inner_loops.append(bottom_rings[-1])
            for z in range(seg_height - 1):
                loop = []
                for s in range(seg_number):
                    loop.append(len(verts))
                    quat = Quaternion((0, 0, 1), (s * stepAngle) + sector_from)
                    verts.append(quat @ Vector((
                        radius_in, 0.0, (z + 1) * stepHeight)))
                inner_loops.append(loop)
            inner_loops.append(top_rings[-1])
            for i in range(len(inner_loops) - 1):
                faces.extend(bridgeLoops(
                    inner_loops[-(i + 1)], inner_loops[-(i + 2)], closed))

        # fill the walls
        if not closed:
            wall_lines_01 = []
            wall_lines_02 = []
            if middlePoint:
                rad_number += 1
            # first wall
            quat = Quaternion((0, 0, 1), sector_from)
            line = []
            for loop in loops:
                line.append(loop[0])
            wall_lines_01.append(line)
            for r in range(rad_number - 1):
                line = []
                line.append(bottom_rings[r + 1][0])
                for h in range(seg_height - 1):
                    line.append(len(verts))
                    verts.append(quat @ Vector((
                        radius_out - ((r + 1) * stepRadius),
                        0.0,
                        (h + 1) * stepHeight)))
                line.append(top_rings[r + 1][0])
                wall_lines_01.append(line)

            if middlePoint:
                wall_lines_01.append(midpoints)
            else:
                line = []
                for loop in inner_loops:
                    line.append(loop[0])
                wall_lines_01.append(line)

            # second wal
            quat = Quaternion((0, 0, 1), sector_to)
            line = []
            for loop in loops:
                line.append(loop[-1])
            wall_lines_02.append(line)
            for r in range(rad_number - 1):
                line = []
                line.append(bottom_rings[r + 1][-1])
                for h in range(seg_height - 1):
                    line.append(len(verts))
                    verts.append(quat @ Vector((
                        radius_out - ((r + 1) * stepRadius),
                        0.0,
                        (h + 1) * stepHeight)))
                line.append(top_rings[r + 1][-1])
                wall_lines_02.append(line)

            if middlePoint:
                wall_lines_02.append(midpoints)
            else:
                line = []
                for loop in inner_loops:
                    line.append(loop[-1])
                wall_lines_02.append(line)

            # filling the walls
            for i in range(len(wall_lines_01) - 1):
                faces.extend(
                    bridgeLoops(
                        wall_lines_01[i], wall_lines_01[i + 1], False))
            for i in range(len(wall_lines_02) - 1):
                faces.extend(
                    bridgeLoops(
                        wall_lines_02[-(i + 1)],
                        wall_lines_02[-(i + 2)],
                        False))

    if centered:
        for vertex in verts:
            vertex[2] -= height / 2

    return verts, edges, faces

def update_WTube (wData):
    return geoGen_WTube (
        radius_out = wData.rad_1,
        radius_in = wData.rad_2,
        height = wData.siz_z,
        use_inner = wData.inn,
        seg_perimeter = wData.seg_1,
        seg_radius = wData.seg_2,
        seg_height = wData.seg_3,
        sector_from = wData.sec_f,
        sector_to = wData.sec_t,
        centered = wData.cent,
        smoothed = wData.smo
    )

# add object W_Plane
class Make_WTube(bpy.types.Operator):
    """Create primitive wTube"""
    bl_idname = "mesh.make_wtube"
    bl_label = "wTube"
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

    radius_in: FloatProperty(
        name="Inner",
        description="Inner radius",
        default=0.0,
        min=0.0,
        soft_min=0.0,
        step=1,
        unit='LENGTH'
    )

    height: FloatProperty(
        name="Height",
        description="Height of the tube",
        default=2.0,
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

    seg_perimeter: IntProperty(
        name="Perimeter",
        description="Periimeter segmentation",
        default=24,
        min=3,
        soft_min=3,
        step=1
    )

    seg_radius: IntProperty(
        name="Radius",
        description="Radius segmentation",
        default=1,
        min=1,
        soft_min=1,
        step=1
    )

    seg_height: IntProperty(
        name="Height",
        description="Height segmentation",
        default=1,
        min=1,
        soft_min=1,
        step=1
    )

    sector_from: FloatProperty(
        name="From",
        description="Section of the cylinder",
        default=0.0,
        min=0.0,
        max=2 * pi,
        soft_min=0.0,
        soft_max=2 * pi,
        step=10,
        unit='ROTATION'
    )

    sector_to: FloatProperty(
        name="To",
        description="Section of the cylinder",
        default=2 * pi,
        min=0.0,
        max=2 * pi,
        soft_min=0.0,
        soft_max=2 * pi,
        step=10,
        unit='ROTATION'
    )

    centered: BoolProperty(
        name="Centered",
        description="Set origin of the cylinder",
        default=True
    )

    smoothed: BoolProperty(
        name="Smooth",
        description="Set origin of the cylinder",
        default=True
    )

    def execute(self, context):

        mesh = bpy.data.meshes.new("wTube")

        wD = mesh.wData
        wD.rad_1 = self.radius_out
        wD.rad_2 = self.radius_in
        wD.siz_z = self.height
        wD.inn = self.use_inner
        wD.seg_1 = self.seg_perimeter
        wD.seg_2 = self.seg_radius
        wD.seg_3 = self.seg_height
        wD.sec_f = self.sector_from
        wD.sec_t = self.sector_to
        wD.cent = self.centered
        wD.smo = self.smoothed
        wD.wType = 'WTUBE'


        mesh.from_pydata(*update_WTube(wD))
        mesh.update()
        
        object_utils.object_data_add(context, mesh, operator=None)

        bpy.ops.object.shade_smooth()
        context.object.data.use_auto_smooth = True
        return {'FINISHED'}

# create UI panel
def draw_WTube_panel(self, context):
    lay_out = self.layout
    lay_out.use_property_split = True
    WData = context.object.data.wData

    lay_out.label(text="Type: wTube", icon='MESH_CYLINDER')

    col = lay_out.column(align=True)
    col.prop(WData, "rad_1", text="Radius Main")
    col.prop(WData, "rad_2", text="Inner")

    lay_out.prop(WData, "siz_z", text="Height")

    col = lay_out.column(align=True)
    col.prop(WData, "sec_f", text="Section From")
    col.prop(WData, "sec_t", text="To")
    
    col = lay_out.column(align=True)
    col.prop(WData, "seg_1", text="Segmentation Main")
    col.prop(WData, "seg_2", text="Cap")
    col.prop(WData, "seg_3", text="Height")

    lay_out.prop(WData, "inn", text="Use inner radius")
    lay_out.prop(WData, "smo", text="Smooth Shading")
    lay_out.prop(WData, "anim", text="Animated")


# register
def reg_wTube():
    bpy.utils.register_class(Make_WTube)
# unregister
def unreg_wTube():
    bpy.utils.unregister_class(Make_WTube)