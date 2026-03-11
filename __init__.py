# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Change Author:__Skii/
# __Created:________15.12.2015______/
# __Last_modified:__10.03.2026______/
# __Version:_1.1_[Sub1(Community_Fix)]/
# __________________________________/

bl_info = {
    "name": "Wonder_Mesh",
    "category": "Object",
    "author": "Vit Prochazka",
    "version": (1, 1),
    "blender": (5, 0),
    "description": "Modify primitives after creation. Fixed for Blender 5.0 with love",
    "warning": "Unexpected bugs can be expected!"
}

import bpy
from bpy.props import EnumProperty

from .W_Plane import registerWPlane, unregisterWPlane, drawWPlanePanel
from .W_Box import registerWBox, unregisterWBox, drawWBoxPanel
from .W_Ring import registerWRing, unregisterWRing, drawWRingPanel
from .W_Tube import registerWTube, unregisterWTube, drawWTubePanel
from .W_Sphere import registerWSphere, unregisterWSphere, drawWSpherePanel
from .W_Screw import registerWScrew, unregisterWScrew, drawWScrewPanel
from .W_Cone import registerWCone, unregisterWCone, drawWConePanel
from .W_Capsule import registerWCapsule, unregisterWCapsule, drawWCapsulePanel
from .W_Torus import registerWTorus, unregisterWTorus, drawWTorusPanel


class WAddMenu(bpy.types.Menu):
    bl_label = "W_Primitives"
    bl_idname = "OBJECT_MT_W_Primitives_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.make_wplane", icon='MESH_PLANE')
        layout.operator("mesh.make_wbox", icon='MESH_CUBE')
        layout.operator("mesh.make_wring", icon='MESH_CIRCLE')
        layout.operator("mesh.make_wsphere", icon='MESH_UVSPHERE')
        layout.operator("mesh.make_wtube", icon='MESH_CYLINDER')
        layout.operator("mesh.make_wcone", icon='MESH_CONE')
        layout.operator("mesh.make_wcapsule", icon='MESH_CAPSULE')
        layout.operator("mesh.make_wtorus", icon='MESH_TORUS')
        layout.operator("mesh.make_wscrew", icon='MOD_SCREW')


def draw_addMenu(self, context):
    layout = self.layout
    layout.menu(WAddMenu.bl_idname)


class WAddPanel(bpy.types.Panel):
    """Creates a Panel in the Toolbar"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Create'
    bl_label = "W_Primitives"
    bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout.column(align=True)
        layout.operator("mesh.make_wplane", icon='MESH_PLANE')
        layout.operator("mesh.make_wbox", icon='MESH_CUBE')
        layout.operator("mesh.make_wring", icon='MESH_CIRCLE')
        layout.operator("mesh.make_wsphere", icon='MESH_UVSPHERE')
        layout.operator("mesh.make_wtube", icon='MESH_CYLINDER')
        layout.operator("mesh.make_wcone", icon='MESH_CONE')
        layout.operator("mesh.make_wcapsule", icon='MESH_CAPSULE')
        layout.operator("mesh.make_wtorus", icon='MESH_TORUS')
        layout.operator("mesh.make_wscrew", icon='MOD_SCREW')


class ConvertWMesh(bpy.types.Operator):
    """Convert WMesh to mesh"""
    bl_idname = "mesh.convert_w_mesh"
    bl_label = "Convert WMesh"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        obj = context.object
        if obj and obj.type == 'MESH':
            obj.data.WType = 'NONE'
        return {'FINISHED'}


class WEditPanel(bpy.types.Panel):
    """Creates a Panel in the data context of the properties editor"""
    bl_label = "WMesh data"
    bl_idname = "DATA_PT_Wlayout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and hasattr(obj.data, "WType")

    def draw(self, context):
        layout = self.layout
        obj = context.object

        WType = getattr(obj.data, "WType", 'NONE')

        if WType == 'NONE':
            layout.label(text="This is regular Mesh")
            return

        if WType == 'WPLANE':
            drawWPlanePanel(self, context)
        elif WType == 'WBOX':
            drawWBoxPanel(self, context)
        elif WType == 'WSCREW':
            drawWScrewPanel(self, context)
        elif WType == 'WRING':
            drawWRingPanel(self, context)
        elif WType == 'WTUBE':
            drawWTubePanel(self, context)
        elif WType == 'WSPHERE':
            drawWSpherePanel(self, context)
        elif WType == 'WCONE':
            drawWConePanel(self, context)
        elif WType == 'WCAPSULE':
            drawWCapsulePanel(self, context)
        elif WType == 'WTORUS':
            drawWTorusPanel(self, context)

        layout.separator()
        layout.operator("mesh.convert_w_mesh", icon='MODIFIER')
        layout.separator()


def register():
    registerWPlane()
    registerWBox()
    registerWScrew()
    registerWRing()
    registerWTube()
    registerWSphere()
    registerWCone()
    registerWCapsule()
    registerWTorus()

    bpy.utils.register_class(WAddPanel)
    bpy.utils.register_class(WAddMenu)
    bpy.utils.register_class(ConvertWMesh)
    bpy.utils.register_class(WEditPanel)

    bpy.types.VIEW3D_MT_mesh_add.prepend(draw_addMenu)

    WTypes = [
        ('NONE', "None", ""),
        ('WPLANE', "WPlane", ""),
        ('WBOX', "WBox", ""),
        ('WSCREW', "WScrew", ""),
        ('WRING', "WRing", ""),
        ('WTUBE', "WTube", ""),
        ('WSPHERE', "WSphere", ""),
        ("WCONE", "WCone", ""),
        ("WCAPSULE", "WCapsule", ""),
        ("WTORUS", "WTorus", "")
    ]

    bpy.types.Mesh.WType = EnumProperty(
        items=WTypes,
        name="WType",
        description="Type of WMesh",
        default='NONE'
    )


def unregister():
    unregisterWPlane()
    unregisterWBox()
    unregisterWScrew()
    unregisterWRing()
    unregisterWTube()
    unregisterWSphere()
    unregisterWCone()
    unregisterWCapsule()
    unregisterWTorus()

    bpy.utils.unregister_class(WAddPanel)
    bpy.utils.unregister_class(WAddMenu)
    bpy.utils.unregister_class(ConvertWMesh)
    bpy.utils.unregister_class(WEditPanel)

    bpy.types.VIEW3D_MT_mesh_add.remove(draw_addMenu)

    del bpy.types.Mesh.WType


if __name__ == "__main__":
    register()
