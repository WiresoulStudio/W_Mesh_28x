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
    PointerProperty,
    EnumProperty
)
from bpy_extras import object_utils
from mathutils import Vector, Quaternion
from math import pi
from .genFunctions import (
    circleVerts as circ_V,
    moveVerts as move_V,
    fanClose,
    subdivide,
    bridgeLoops
)
from .W_Bases import baseHedron


def primitive_UVSphere(
                radius = 1.0,
                segments = 24,
                rings = 12):

    verts = []
    edges = []
    faces = []

    loops = []

    # create top and bottom verts
    verts.append(Vector((0.0, 0.0, radius)))
    verts.append(Vector((0.0, 0.0, -radius)))

    # calculate angles
    UAngle = (2*pi)/segments
    VAngle = pi/rings

    # create rings
    for v in range(rings - 1):
        loop = []
        quatV = Quaternion((0, -1, 0), VAngle * (v + 1))
        baseVect = quatV @ Vector((0.0, 0.0, -radius))
        for u in range(segments):
            loop.append(len(verts))
            quatU = Quaternion((0, 0, 1), UAngle * u)
            verts.append(quatU @ baseVect)
        loops.append(loop)

    # create faces
    for i in range(rings - 2):
        faces.extend(bridgeLoops(loops[i], loops[i + 1], True))

    # fill top
    ring = loops[-1]
    for i in range(segments):
        if (i == segments - 1):
            faces.append((ring[i], ring[0], 0))
        else:
            faces.append((ring[i], ring[i + 1], 0))

    # fill bottom
    ring = loops[0]
    for i in range(segments):
        if (i == segments - 1):
            faces.append((ring[0], ring[i], 1))
        else:
            faces.append((ring[i + 1], ring[i], 1))

    return verts, edges, faces



def primitive_polySphere(
                    base = "CUBE",
                    radius = 1.0,
                    divisions = 2,
                    tris = True):

    verts, edges, faces = baseHedron(base)

    for vert in verts:
        vert.normalize()
        vert *= radius

    if base == "CUBE":
        tris = False

    for i in range(divisions):
        verts, edges, faces = subdivide(verts, edges, faces, tris)

        # normalize
        for vert in verts:
            vert.normalize()
            vert *= radius

    return verts, edges, faces


def update_WSphere (wData):
    if wData.sBase == "UV":
        return primitive_UVSphere(
            radius = wData.rad_1,
            segments = wData.seg_1,
            rings = wData.seg_2
        )
    else:
        return primitive_polySphere(
            base = wData.sBase,
            radius = wData.rad_1,
            divisions = wData.seg_3,
            tris = wData.inn
        )
        
    

# add object W_Plane
class Make_WSphere(bpy.types.Operator):
    """Create primitive wSphere"""
    bl_idname = "mesh.make_wsphere"
    bl_label = "wSphere"
    bl_options = {'UNDO', 'REGISTER'}

    radius: FloatProperty(
        name="Radius",
        description="Radius of the Sphere",
        default=1.0,
        min=0.0,
        soft_min=0.0001,
        step=1,
        unit='LENGTH'
    )

    segments: IntProperty(
        name="Segments",
        description="Segments on diametr",
        default=24,
        min=3,
        soft_min=3,
        step=1,
        subtype='NONE'
    )

    rings: IntProperty(
        name="Rings",
        description="Rings",
        default=12,
        min=2,
        soft_min=2,
        step=1,
        subtype='NONE'
    )

    divisions: IntProperty(
        name="Division",
        description="Divisions of the base mesh",
        default=2,
        min=0,
        soft_min=0,
        step=1,
        subtype='NONE'
    )

    Topos = [
        ('UV', "UV", "", 1),
        ('TETRA', "Tetrahedron", "", 2),
        ('CUBE', "Cube", "", 3),
        ('OCTA', "Octahedron", "", 4),
        ('ICOSA', "Icosahedron", "", 5)
    ]

    base: EnumProperty(
        items = Topos,
        name = "Topology",
        description = "Type of sphere topology",
        default = 'CUBE'
    )

    smoothed: BoolProperty(
        name="Smooth",
        description="Smooth shading",
        default=True
    )

    tris: BoolProperty(
        name="Tris",
        description="Triangulate divisions",
        default=False
    )

    def execute(self, context):

        mesh = bpy.data.meshes.new("wSphere")

        wD = mesh.wData
        wD.sBase = self.base
        wD.rad_1 = self.radius
        wD.seg_1 = self.segments
        wD.seg_2 = self.rings
        wD.seg_3 = self.divisions
        wD.inn = self.tris
        wD.smo = self.smoothed
        wD.wType = 'WSPHERE'


        mesh.from_pydata(*update_WSphere(wD))
        mesh.update()
        
        object_utils.object_data_add(context, mesh, operator=None)

        bpy.ops.object.shade_smooth()
        context.object.data.use_auto_smooth = True
        context.object.data.auto_smooth_angle = 1.0
        return {'FINISHED'}

# create UI panel
def draw_WSphere_panel(self, context):
    lay_out = self.layout
    lay_out.use_property_split = True
    WData = context.object.data.wData

    lay_out.label(text="Type: wSphere", icon='MESH_UVSPHERE')

    lay_out.prop(WData, "rad_1", text="Radius")
    lay_out.prop(WData, "sBase", text="Topology")

    if WData.sBase == "UV":
        col = lay_out.column(align=True)
        col.prop(WData, "seg_1", text="Segments")
        col.prop(WData, "seg_2", text="Rings")
    
    else:
        lay_out.prop(WData, "seg_3", text="Divisions")
        lay_out.prop(WData, "inn", text="Triangulate")
    

    lay_out.prop(WData, "smo", text="Smooth Shading")
    lay_out.prop(WData, "anim", text="Animated")


# register
def reg_wSphere():
    bpy.utils.register_class(Make_WSphere)
# unregister
def unreg_wSphere():
    bpy.utils.unregister_class(Make_WSphere)