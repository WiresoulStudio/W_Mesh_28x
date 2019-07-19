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
from math import pi as PI
from .genFunctions import (
    circleVerts as circ_V,
    moveVerts as move_V,
    fanClose,
    bridgeLoops,
    create_mesh_object
)

# generate geometry
def geoGen_WCone (
    radius_main,
    radius_top,
    height,
    seg_perimeter,
    seg_height,
    seg_radius,
    centered,
    smoothed):
    
    # Prepare empty lists
    verts = []
    edges = []
    faces = []

    loops = []

    # Set minimums
    if seg_perimeter < 3:
        seg_perimeter = 3
    if seg_height < 1:
        seg_height = 1
    if seg_radius < 1:
        seg_radius = 1

    # Add top and bottom center vertices
    verts.append(Vector((0, 0, 0)))
    verts.append(Vector((0, 0, height)))

    if radius_top == 0 and radius_main == 0:
        edges.append((0, 1))
        return verts, edges, faces

    # Create base segmentation loops
    if radius_main > 0:
        if seg_radius > 1:
            step = radius_main / seg_radius
            for i in range(1, seg_radius):
                newVerts, loop = circ_V(i * step, seg_perimeter, len(verts))
                verts.extend(newVerts)
                loops.append(loop)

        # Create the base corner circle
        newVerts, loop = circ_V(radius_main, seg_perimeter, len(verts))
        verts.extend(newVerts)
        loops.append(loop)

    # Create the side segmentation loops
    if seg_height > 1:
        heightStep = height / seg_height
        radiusStep = (radius_top - radius_main) / seg_height
        for i in range(1, seg_height):
            newRadius = radius_main + (i * radiusStep)
            newVerts, loop = circ_V(newRadius, seg_perimeter, len(verts))
            move_V(newVerts, Vector((0, 0, heightStep * i)))
            verts.extend(newVerts)
            loops.append(loop)

    # Create top corner circle
    if radius_top > 0:
        newVerts, loop = circ_V(radius_top, seg_perimeter, len(verts))
        move_V(newVerts, Vector((0, 0, height)))
        verts.extend(newVerts)
        loops.append(loop)

        # Create the top segmentation loops
        if seg_radius > 1:
            step = radius_top / seg_radius
            for i in range(1, seg_radius):
                newRadius = radius_top - (i * step)
                newVerts, loop = circ_V(newRadius, seg_perimeter, len(verts))
                move_V(newVerts, Vector((0, 0, height)))
                verts.extend(newVerts)
                loops.append(loop)

    # Close caps
    faces.extend(fanClose(loops[0], 0, closed = True, flipped = True))
    faces.extend(fanClose(loops[-1], 1))

    # Bridge all loops
    for i in range(1, len(loops)):
        faces.extend(bridgeLoops(loops[i - 1], loops[i], True))

    if centered:
        move_V(verts, Vector((0, 0, -height / 2)))

    return verts, edges, faces

def update_WCone (wData):
    return geoGen_WCone (
        radius_main = wData.rad_1,
        radius_top = wData.rad_2,
        height = wData.siz_z,
        seg_perimeter = wData.seg_1,
        seg_height = wData.seg_2,
        seg_radius = wData.seg_3,
        centered = wData.cent,
        smoothed = wData.smo
    )

# add object W_Plane
class Make_WCone(bpy.types.Operator):
    """Create primitive wCone"""
    bl_idname = "mesh.make_wcone"
    bl_label = "wCone"
    bl_options = {'UNDO', 'REGISTER'}

    radius_top: FloatProperty(
        name = "Radius top",
        description = "Top Radius",
        default = 0.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        precision = 2,
        unit = "LENGTH"
    )

    radius_main: FloatProperty(
        name = "Radius bottom",
        description = "Bottom Radius",
        default = 1.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        precision = 2,
        unit = "LENGTH"
    )

    height: FloatProperty(
        name = "Height",
        description = "Height of the cone",
        default = 2.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        precision = 2,
        unit = "LENGTH"
    )

    seg_perimeter: IntProperty(
        name = "Perim Segments",
        description = "Subdivision on perimeter",
        default = 24,
        min = 3,
        soft_min = 3,
        step = 1,
        subtype = 'NONE'
    )

    seg_height: IntProperty(
        name = "Height Segments",
        description = "Subdivision of the height",
        default = 1,
        min = 1,
        soft_min = 1,
        step = 1,
        subtype = 'NONE'
    )

    seg_radius: IntProperty(
        name = "Radius Segments",
        description = "Subdivision of the radius",
        default = 1,
        min = 1,
        soft_min = 1,
        step = 1,
        subtype = 'NONE'
    )

    centered: BoolProperty(
        name = "Centered",
        description = "Set origin of the cone",
        default = False
    )

    def execute(self, context):

        mesh = bpy.data.meshes.new("wCone")

        wD = mesh.wData
        wD.rad_1 = self.radius_main
        wD.rad_2 = self.radius_top
        wD.siz_z = self.height
        wD.seg_1 = self.seg_perimeter
        wD.seg_2 = self.seg_height
        wD.seg_3 = self.seg_radius
        wD.cent = self.centered
        wD.smo = True
        wD.wType = 'WCONE'


        mesh.from_pydata(*update_WCone(wD))
        mesh.update()
        
        object_utils.object_data_add(context, mesh, operator=None)

        bpy.ops.object.shade_smooth()
        context.object.data.use_auto_smooth = True
        context.object.data.auto_smooth_angle = 1.0
        return {'FINISHED'}

# create UI panel
def draw_WCone_panel(self, context):
    lay_out = self.layout
    lay_out.use_property_split = True
    WData = context.object.data.wData

    lay_out.label(text="Type: wCone", icon='MESH_CONE')

    col = lay_out.column(align=True)
    col.prop(WData, "rad_2", text="Radius Top")
    col.prop(WData, "rad_1", text="Radius Main")
    col.prop(WData, "siz_z", text="Height")
    
    col = lay_out.column(align=True)
    col.prop(WData, "seg_1", text="Segmentation Main")
    col.prop(WData, "seg_2", text="Vertical")
    col.prop(WData, "seg_3", text="Caps")

    lay_out.prop(WData, "cent", text="Centered")
    lay_out.prop(WData, "smo", text="Smooth Shading")
    lay_out.prop(WData, "anim", text="Animated")


# register
def reg_wCone():
    bpy.utils.register_class(Make_WCone)
# unregister
def unreg_wCone():
    bpy.utils.unregister_class(Make_WCone)