# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Change Author:__Skii____________/
# __Created:________13.08.2017______/
# __Last_modified:__10.03.2026______/
# __Version:_0.2_Sub1(Community_Fix)/
# __________________________________/

import bpy
from bpy.props import FloatProperty, IntProperty, PointerProperty, EnumProperty, BoolProperty
from mathutils import Vector, Quaternion
from math import pi
from .gen_func import bridgeLoops, create_mesh_object, subdivide
from .W_Bases import baseHedron


WSphere_defaults = {
    "radius": 1.0,
    "segments": 24,
    "rings": 12,
    "base": 'CUBE',
    "divisions": 2,
    "tris": False,
    "smoothed": True
}


def primitive_UVSphere(radius=1.0, segments=24, rings=12):

    verts = []
    edges = []
    faces = []
    loops = []

    verts.append(Vector((0.0, 0.0, radius)))
    verts.append(Vector((0.0, 0.0, -radius)))

    UAngle = (2*pi)/segments
    VAngle = pi/rings

    for v in range(rings - 1):

        loop = []

        quatV = Quaternion((0, -1, 0), VAngle * (v + 1))
        baseVect = quatV @ Vector((0.0, 0.0, -radius))

        for u in range(segments):

            loop.append(len(verts))
            quatU = Quaternion((0, 0, 1), UAngle * u)

            verts.append(quatU @ baseVect)

        loops.append(loop)

    for i in range(rings - 2):
        faces.extend(bridgeLoops(loops[i], loops[i + 1], True))

    ring = loops[-1]

    for i in range(segments):

        if i == segments - 1:
            faces.append((ring[i], ring[0], 0))
        else:
            faces.append((ring[i], ring[i + 1], 0))

    ring = loops[0]

    for i in range(segments):

        if i == segments - 1:
            faces.append((ring[0], ring[i], 1))
        else:
            faces.append((ring[i + 1], ring[i], 1))

    return verts, edges, faces


def primitive_polySphere(base='CUBE', radius=1.0, divisions=2, tris=True):

    verts, edges, faces = baseHedron(base)

    for vert in verts:
        vert.normalize()
        vert *= radius

    if base == "CUBE":
        tris = False

    for i in range(divisions):

        verts, edges, faces = subdivide(verts, edges, faces, tris)

        for vert in verts:
            vert.normalize()
            vert *= radius

    return verts, edges, faces


def update_sphere(self, context):

    if context.object is None:
        return

    mesh = context.object.data

    if self.base == 'UV':

        verts, edges, faces = primitive_UVSphere(
            self.radius,
            self.segments,
            self.rings
        )

    else:

        verts, edges, faces = primitive_polySphere(
            self.base,
            self.radius,
            self.divisions,
            self.tris
        )

    mesh.clear_geometry()
    mesh.from_pydata(verts, edges, faces)

    if self.smoothed:

        for poly in mesh.polygons:
            poly.use_smooth = True

    mesh.update()


class WSphereData(bpy.types.PropertyGroup):

    radius: FloatProperty(
        name="Radius",
        default=1.0,
        min=0.0,
        update=update_sphere
    )

    segments: IntProperty(
        name="Segments",
        default=24,
        min=3,
        update=update_sphere
    )

    rings: IntProperty(
        name="Rings",
        default=12,
        min=2,
        update=update_sphere
    )

    divisions: IntProperty(
        name="Divisions",
        default=2,
        min=0,
        update=update_sphere
    )

    Topos = [
        ('UV', "UV", ""),
        ('TETRA', "Tetrahedron", ""),
        ('CUBE', "Cube", ""),
        ('OCTA', "Octahedron", ""),
        ('ICOSA', "Icosahedron", "")
    ]

    base: EnumProperty(
        items=Topos,
        name="Topology",
        default='CUBE',
        update=update_sphere
    )

    smoothed: BoolProperty(
        name="Smooth",
        default=True,
        update=update_sphere
    )

    tris: BoolProperty(
        name="Tris",
        default=False,
        update=update_sphere
    )


class Make_WSphere(bpy.types.Operator):

    bl_idname = "mesh.make_wsphere"
    bl_label = "WSphere"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):

        verts, edges, faces = primitive_polySphere()

        obj = create_mesh_object(context, verts, edges, faces, "WSphere")
        mesh = obj.data

        mesh.WType = 'WSPHERE'

        mesh.WSphere.radius = WSphere_defaults["radius"]
        mesh.WSphere.segments = WSphere_defaults["segments"]
        mesh.WSphere.rings = WSphere_defaults["rings"]
        mesh.WSphere.base = WSphere_defaults["base"]
        mesh.WSphere.divisions = WSphere_defaults["divisions"]
        mesh.WSphere.tris = WSphere_defaults["tris"]
        mesh.WSphere.smoothed = WSphere_defaults["smoothed"]

        bpy.ops.object.shade_smooth()

        return {'FINISHED'}


def drawWSpherePanel(self, context):

    layout = self.layout
    WData = context.object.data.WSphere

    layout.label(text="Type: WSphere", icon='MESH_UVSPHERE')

    row = layout.row()

    col = row.column()
    col.prop(WData, "radius")
    col.prop(WData, "base")

    col = row.column()

    if WData.base == 'UV':
        col.prop(WData, "segments")
        col.prop(WData, "rings")
    else:
        col.prop(WData, "divisions")
        col.prop(WData, "tris")

    layout.prop(WData, "smoothed")


def registerWSphere():

    bpy.utils.register_class(Make_WSphere)
    bpy.utils.register_class(WSphereData)

    bpy.types.Mesh.WSphere = PointerProperty(type=WSphereData)


def unregisterWSphere():

    bpy.utils.unregister_class(Make_WSphere)
    bpy.utils.unregister_class(WSphereData)

    del bpy.types.Mesh.WSphere
