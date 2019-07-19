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
def geoGen_WCapsule (
    radius,
    height,
    seg_perimeter,
    seg_height,
    seg_caps,
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
    if seg_caps < 1:
        seg_caps = 1
    if radius > height / 2:
        radius = height / 2

    # Add top and bottom center vertices
    verts.append(Vector((0, 0, 0)))
    verts.append(Vector((0, 0, height)))

    # Create bootom cap segmentation loops
    if seg_caps > 1:
        angleStep = PI / (2 * seg_caps)
        for i in range(1, seg_caps):
            # find the radius and height
            quat = Quaternion((0, -1, 0), i * angleStep)
            helperVect = quat @ Vector((0, 0, -radius))
            segmentRadius = helperVect.x
            segmentHeight = radius + helperVect.z
            # create the ring
            newVerts, loop = circ_V(segmentRadius, seg_perimeter, len(verts))
            move_V(newVerts, Vector((0, 0, segmentHeight)))
            verts.extend(newVerts)
            loops.append(loop)

    # Create the base corner circle
    newVerts, loop = circ_V(radius, seg_perimeter, len(verts))
    move_V(newVerts, Vector((0, 0, radius)))
    verts.extend(newVerts)
    loops.append(loop)

    # Create the side segmentation loops
    if height > 2 * radius:
        if seg_height > 1:
            heightStep = (height - (2 * radius)) / seg_height
            for i in range(1, seg_height):
                newHeight = (i * heightStep) + radius
                newVerts, loop = circ_V(radius, seg_perimeter, len(verts))
                move_V(newVerts, Vector((0, 0, newHeight)))
                verts.extend(newVerts)
                loops.append(loop)

    # Create top corner circle
        newVerts, loop = circ_V(radius, seg_perimeter, len(verts))
        move_V(newVerts, Vector((0, 0, height - radius)))
        verts.extend(newVerts)
        loops.append(loop)

    # Create top cap segmentation loops
    if seg_caps > 1:
        angleStep = PI / (2 * seg_caps)
        for i in range(1, seg_caps):
            # find the radius and height
            quat = Quaternion((0, -1, 0), i * angleStep)
            helperVect = quat @ Vector((radius, 0, 0))
            segmentRadius = helperVect.x
            segmentHeight = height - radius + helperVect.z
            # create the ring
            newVerts, loop = circ_V(segmentRadius, seg_perimeter, len(verts))
            move_V(newVerts, Vector((0, 0, segmentHeight)))
            verts.extend(newVerts)
            loops.append(loop)

    # Close caps
    faces.extend(fanClose(loops[0], 0, flipped = True))
    faces.extend(fanClose(loops[-1], 1))

    # Bridge all loops
    for i in range(1, len(loops)):
        faces.extend(bridgeLoops(loops[i - 1], loops[i], True))

    if centered:
        move_V(verts, Vector((0, 0, -height / 2)))

    return verts, edges, faces

def update_WCapsule (wData):
    return geoGen_WCapsule (
        radius = wData.rad_1,
        height = wData.siz_z,
        seg_perimeter = wData.seg_1,
        seg_height = wData.seg_2,
        seg_caps = wData.seg_3,
        centered = wData.cent,
        smoothed = wData.smo
    )

# add object W_Plane
class Make_WCapsule(bpy.types.Operator):
    """Create primitive wCapsule"""
    bl_idname = "mesh.make_wcapsule"
    bl_label = "wCapsule"
    bl_options = {'UNDO', 'REGISTER'}

    radius: FloatProperty(
        name = "Radius",
        description = "Radius",
        default = 0.5,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit = "LENGTH"
    )

    height: FloatProperty(
        name = "Height",
        description = "Height of the capsule",
        default = 2.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
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

    seg_caps: IntProperty(
        name = "Caps Segments",
        description = "Subdivision of the caps",
        default = 6,
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

    smoothed: BoolProperty(
        name = "Smooth",
        description = "Set smooth shading",
        default = True
    )

    def execute(self, context):

        verts, edges, faces = geoGen_WCapsule(
            radius = self.radius,
            height = self.height,
            seg_perimeter = self.seg_perimeter,
            seg_height = self.seg_height,
            seg_caps = self.seg_caps,
            centered = self.centered,
            smoothed = self.smoothed
        )
        create_mesh_object(context, verts, edges, faces, "wCapsule")

        wD = context.object.data.wData
        wD.rad_1 = self.radius
        wD.siz_z = self.height
        wD.seg_1 = self.seg_perimeter
        wD.seg_2 = self.seg_height
        wD.seg_3 = self.seg_caps
        wD.cent = self.centered
        wD.smo = self.smoothed
        wD.wType = 'WCAPSULE'

        bpy.ops.object.shade_smooth()
        context.object.data.use_auto_smooth = True
        return {'FINISHED'}

# create UI panel
def draw_WCapsule_panel(self, context):
    lay_out = self.layout
    lay_out.use_property_split = True
    WData = context.object.data.wData

    lay_out.label(text="Type: wCapsule", icon='MESH_CAPSULE')

    col = lay_out.column(align=True)
    col.prop(WData, "rad_1", text="Radius")
    col.prop(WData, "siz_z", text="Height")
    
    col = lay_out.column(align=True)
    col.prop(WData, "seg_1", text="Segmentation Main")
    col.prop(WData, "seg_2", text="Vertical")
    col.prop(WData, "seg_3", text="Caps")

    lay_out.prop(WData, "cent", text="Centered")
    lay_out.prop(WData, "smo", text="Smooth Shading")
    lay_out.prop(WData, "anim", text="Animated")


# register
def reg_wCapsule():
    bpy.utils.register_class(Make_WCapsule)
# unregister
def unreg_wCapsule():
    bpy.utils.unregister_class(Make_WCapsule)