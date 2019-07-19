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
def geoGen_WPlane (size_x, size_y, seg_x, seg_y, centered):
    
    # set initial values
    if seg_x < 1: seg_x = 1
    if seg_y < 1: seg_y = 1

    verts = []
    edges = []
    faces = []
    lines = []

    # precompute 
    segSize_X = size_x / seg_x
    segSize_Y = size_y / seg_y

    # compute vertices
    for i in range(seg_y + 1):
        line = []
        for j in range(seg_x + 1):
            line.append(len(verts))
            verts.append(Vector((j * segSize_X, i * segSize_Y, 0.0)))
        lines.append(line)

    # fill faces
    for i in range(len(lines)-1):
        faces.extend(bridgeLoops(lines[i], lines[i + 1], False))

    if centered:
        half_x = size_x / 2
        half_y = size_y / 2
        for vertex in verts:
            vertex[0] -= half_x
            vertex[1] -= half_y

    return verts, edges, faces

def update_wPlane (wData):
    return geoGen_WPlane (
        size_x=wData.siz_x,
        size_y=wData.siz_y,
        seg_x=wData.seg_1,
        seg_y=wData.seg_2,
        centered=wData.cent
    )

# add object W_Plane
class Make_WPlane(bpy.types.Operator):
    """Create primitive wPlane"""
    bl_idname = "mesh.make_wplane"
    bl_label = "wPlane"
    bl_options = {'UNDO', 'REGISTER'}

    size_x: FloatProperty(
        name = "Width (X)",
        description = "Size of the wPlane",
        default = 2.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit='LENGTH'
    )

    size_y: FloatProperty(
        name = "Length (Y)",
        description = "Size of the wPlane",
        default = 2.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit='LENGTH'
    )

    seg_x: IntProperty(
        name = "Segments X",
        description = "Segmentation of the wPlane",
        default = 1,
        min = 1,
        soft_min = 1,
        step = 1
    )

    seg_y: IntProperty(
        name = "Segments Y",
        description = "Segmentation of the wPlane",
        default = 1,
        min = 1,
        soft_min = 1,
        step = 1
    )

    centered: BoolProperty(
        name = "Centered",
        description = "Where is origin of the wPlane",
        default = True
    )

    def execute(self, context):

        verts, edges, faces = geoGen_WPlane(
            size_x=self.size_x,
            size_y=self.size_y,
            seg_x=self.seg_x,
            seg_y=self.seg_y,
            centered=self.centered
        )
        create_mesh_object(context, verts, edges, faces, "wPlane")

        wD = context.object.data.wData
        wD.siz_x = self.size_x
        wD.siz_y = self.size_y
        wD.seg_1 = self.seg_x
        wD.seg_2 = self.seg_y
        wD.cent = self.centered
        wD.wType = 'WPLANE'
        return {'FINISHED'}
# create UI panel
def draw_wPlane_panel(self, context):
    lay_out = self.layout
    lay_out.use_property_split = True
    WData = context.object.data.wData

    lay_out.label(text="Type: wPlane", icon='MESH_PLANE')

    col = lay_out.column(align=True)
    col.prop(WData, "siz_x", text="Size X")
    col.prop(WData, "siz_y", text="Y")
    
    col = lay_out.column(align=True)
    col.prop(WData, "seg_1", text="Segmentation X")
    col.prop(WData, "seg_2", text="Y")

    lay_out.prop(WData, "cent", text="Centered")
    lay_out.prop(WData, "anim", text="Animated")


# register
def reg_wPlane():
    bpy.utils.register_class(Make_WPlane)
# unregister
def unreg_wPlane():
    bpy.utils.unregister_class(Make_WPlane)
