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
from mathutils import Vector
from .genFunctions import bridgeLoops, create_mesh_object

# generate geometry
def geoGen_WBox (size_x, size_y, size_z, seg_x, seg_y, seg_z, centered):
    
    if seg_x < 1: seg_x = 1
    if seg_y < 1: seg_y = 1
    if seg_z < 1: seg_z = 1

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
        loop.append(bottom_lines[i + 1][- 1])
    for i in range(seg_x + 1):
        loop.append(bottom_lines[- 1][-(i + 1)])
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
            verts.append(Vector((
                size_x - (i * dist_x), size_y, (z + 1) * dist_z)))
        for i in range(seg_y - 1):
            loop.append(len(verts))
            verts.append(Vector((
                0.0, size_y - ((i + 1) * dist_y), (z + 1) * dist_z)))
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

    # faces bottom
    for i in range(seg_y):
        faces.extend(bridgeLoops(bottom_lines[i+1], bottom_lines[i], False))

    # faces top
    for i in range(seg_y):
        faces.extend(bridgeLoops(top_lines[i], top_lines[i + 1], False))

    # faces sides
    for i in range(seg_z):
        faces.extend(bridgeLoops(loops[i], loops[i + 1], True))

    if centered:
        half_x = size_x / 2
        half_y = size_y / 2
        half_z = size_z / 2
        for vertex in verts:
            vertex -= Vector((half_x, half_y, half_z))

    return verts, edges, faces

def update_WBox (wData):
    return geoGen_WBox (
        size_x=wData.siz_x,
        size_y=wData.siz_y,
        size_z=wData.siz_z,
        seg_x=wData.seg_1,
        seg_y=wData.seg_2,
        seg_z=wData.seg_3,
        centered=wData.cent
    )

# add object W_Plane
class Make_WBox(bpy.types.Operator):
    """Create primitive wBox"""
    bl_idname = "mesh.make_wbox"
    bl_label = "wBox"
    bl_options = {'UNDO', 'REGISTER'}

    size_x: FloatProperty(
        name = "Width (X)",
        description = "Size of the WBox",
        default = 2.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit='LENGTH'
    )

    size_y: FloatProperty(
        name = "Length (Y)",
        description = "Size of the WBox",
        default = 2.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit='LENGTH'
    )

    size_z: FloatProperty(
        name = "Height (Z)",
        description = "Size of the WBox",
        default = 2.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit='LENGTH'
    )

    seg_x: IntProperty(
        name = "Segments X",
        description = "Segmentation of the WBox",
        default = 1,
        min = 1,
        soft_min = 1,
        step = 1
    )

    seg_y: IntProperty(
        name = "Segments Y",
        description = "Segmentation of the WBox",
        default = 1,
        min = 1,
        soft_min = 1,
        step = 1
    )

    seg_z: IntProperty(
        name = "Segments Z",
        description = "Segmentation of the WBox",
        default = 1,
        min = 1,
        soft_min = 1,
        step = 1
    )

    centered: BoolProperty(
        name = "Centered",
        description = "Where is origin of the WBox",
        default = True
    )

    def execute(self, context):

        verts, edges, faces = geoGen_WBox(
            size_x=self.size_x,
            size_y=self.size_y,
            size_z=self.size_z,
            seg_x=self.seg_x,
            seg_y=self.seg_y,
            seg_z=self.seg_z,
            centered=self.centered
        )
        create_mesh_object(context, verts, edges, faces, "wBox")

        wD = context.object.data.wData
        wD.siz_x = self.size_x
        wD.siz_y = self.size_y
        wD.siz_z = self.size_z
        wD.seg_1 = self.seg_x
        wD.seg_2 = self.seg_y
        wD.seg_3 = self.seg_z
        wD.cent = self.centered
        wD.wType = 'WBOX'
        return {'FINISHED'}
# create UI panel
def draw_WBox_panel(self, context):
    lay_out = self.layout
    lay_out.use_property_split = True
    WData = context.object.data.wData

    lay_out.label(text="Type: wBox", icon='MESH_CUBE')

    col = lay_out.column(align=True)
    col.prop(WData, "siz_x", text="Size X")
    col.prop(WData, "siz_y", text="Y")
    col.prop(WData, "siz_z", text="Z")
    
    col = lay_out.column(align=True)
    col.prop(WData, "seg_1", text="Segmentation X")
    col.prop(WData, "seg_2", text="Y")
    col.prop(WData, "seg_3", text="Z")

    lay_out.prop(WData, "cent", text="Centered")
    lay_out.prop(WData, "anim", text="Animated")


# register
def reg_wBox():
    bpy.utils.register_class(Make_WBox)
# unregister
def unreg_wBox():
    bpy.utils.unregister_class(Make_WBox)