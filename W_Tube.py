# __________________________________/
# __Author:_________Vit_Prochazka___/
# __Change Author:__Skii____________/
# __Created:________16.12.2015______/
# __Last_modified:__11.03.2026______/
# __Version:_0.3_Sub1(Community_Fix)/
# __________________________________/

import bpy
from bpy.props import FloatProperty, IntProperty, BoolProperty, PointerProperty
from mathutils import Quaternion, Vector
from .gen_func import bridgeLoops, create_mesh_object
from math import pi


WTube_Defaults = {
    "radius_out": 1.0,
    "radius_in": 0.0,
    "height": 2.0,
    "use_inner": True,
    "seg_perimeter": 24,
    "seg_radius": 1,
    "seg_height": 1,
    "sector_from": 0.0,
    "sector_to": 2 * pi,
    "centered": True,
    "smoothed": True
}


def primitive_Tube(
        radius_out=1.0,
        radius_in=0.0,
        height=2.0,
        use_inner=True,
        seg_perimeter=24,
        seg_radius=1,
        seg_height=1,
        sector_from=0.0,
        sector_to=2*pi,
        centered=True,
        smoothed=True):

    verts=[]
    edges=[]
    faces=[]

    top_rings=[]
    bottom_rings=[]
    loops=[]
    inner_loops=[]
    midpoints=[]

    if radius_out < radius_in:
        radius_in, radius_out = radius_out, radius_in

    if sector_from > sector_to:
        sector_to, sector_from = sector_from, sector_to

    if radius_out - radius_in < 0.0001:
        use_inner=False

    if seg_perimeter < 3:
        seg_perimeter=3

    stepAngle=(sector_to-sector_from)/seg_perimeter
    stepRadius=(radius_out-radius_in)/seg_radius
    stepHeight=height/seg_height

    middlePoint=radius_in <= 0.0001
    closed=(sector_to-sector_from)>=2*pi

    seg_number=seg_perimeter if closed else seg_perimeter+1
    rad_number=seg_radius if not middlePoint else seg_radius-1

    # outer wall
    for z in range(seg_height+1):
        loop=[]
        for s in range(seg_number):
            loop.append(len(verts))
            quat=Quaternion((0,0,1),(s*stepAngle)+sector_from)
            verts.append(quat @ Vector((radius_out,0,z*stepHeight)))
        loops.append(loop)

    for i in range(len(loops)-1):
        faces.extend(bridgeLoops(loops[i],loops[i+1],closed))

    if use_inner:

        # caps
        for z in range(2):

            if z==0:
                bottom_rings.append(loops[0])
            else:
                top_rings.append(loops[-1])

            for r in range(rad_number):
                ring=[]
                for s in range(seg_number):
                    ring.append(len(verts))
                    quat=Quaternion((0,0,1),(s*stepAngle)+sector_from)
                    verts.append(quat @ Vector(
                        (radius_out-((r+1)*stepRadius),0,z*height)))

                if z==0:
                    bottom_rings.append(ring)
                else:
                    top_rings.append(ring)

        for i in range(len(top_rings)-1):
            faces.extend(bridgeLoops(top_rings[i],top_rings[i+1],closed))

        for i in range(len(bottom_rings)-1):
            faces.extend(
                bridgeLoops(bottom_rings[-(i+1)],bottom_rings[-(i+2)],closed))

        # center fill
        if middlePoint:

            if closed:
                for z in range(2):
                    midpoints.append(len(verts))
                    verts.append(Vector((0,0,z*height)))
            else:
                for z in range(seg_height+1):
                    midpoints.append(len(verts))
                    verts.append(Vector((0,0,z*stepHeight)))

            for s in range(seg_number-1):

                faces.append((
                    bottom_rings[-1][s],
                    midpoints[0],
                    bottom_rings[-1][s+1]))

                faces.append((
                    top_rings[-1][s],
                    top_rings[-1][s+1],
                    midpoints[-1]))

            if closed:

                faces.append((
                    bottom_rings[-1][-1],
                    midpoints[0],
                    bottom_rings[-1][0]))

                faces.append((
                    top_rings[-1][-1],
                    top_rings[-1][0],
                    midpoints[-1]))

        else:

            inner_loops.append(bottom_rings[-1])

            for z in range(seg_height-1):

                loop=[]
                for s in range(seg_number):

                    loop.append(len(verts))

                    quat=Quaternion((0,0,1),(s*stepAngle)+sector_from)

                    verts.append(quat @ Vector(
                        (radius_in,0,(z+1)*stepHeight)))

                inner_loops.append(loop)

            inner_loops.append(top_rings[-1])

            for i in range(len(inner_loops)-1):

                faces.extend(
                    bridgeLoops(
                        inner_loops[-(i+1)],
                        inner_loops[-(i+2)],
                        closed))

        # sector wall closure
        if not closed:

            wall_lines_01=[]
            wall_lines_02=[]

            if middlePoint:
                rad_number+=1

            quat=Quaternion((0,0,1),sector_from)

            line=[]
            for loop in loops:
                line.append(loop[0])
            wall_lines_01.append(line)

            for r in range(rad_number-1):

                line=[]
                line.append(bottom_rings[r+1][0])

                for h in range(seg_height-1):

                    line.append(len(verts))

                    verts.append(quat @ Vector(
                        (radius_out-((r+1)*stepRadius),
                         0,
                         (h+1)*stepHeight)))

                line.append(top_rings[r+1][0])
                wall_lines_01.append(line)

            if middlePoint:
                wall_lines_01.append(midpoints)

            else:
                line=[]
                for loop in inner_loops:
                    line.append(loop[0])
                wall_lines_01.append(line)

            quat=Quaternion((0,0,1),sector_to)

            line=[]
            for loop in loops:
                line.append(loop[-1])
            wall_lines_02.append(line)

            for r in range(rad_number-1):

                line=[]
                line.append(bottom_rings[r+1][-1])

                for h in range(seg_height-1):

                    line.append(len(verts))

                    verts.append(quat @ Vector(
                        (radius_out-((r+1)*stepRadius),
                         0,
                         (h+1)*stepHeight)))

                line.append(top_rings[r+1][-1])
                wall_lines_02.append(line)

            if middlePoint:
                wall_lines_02.append(midpoints)

            else:
                line=[]
                for loop in inner_loops:
                    line.append(loop[-1])
                wall_lines_02.append(line)

            for i in range(len(wall_lines_01)-1):

                faces.extend(
                    bridgeLoops(
                        wall_lines_01[i],
                        wall_lines_01[i+1],
                        False))

            for i in range(len(wall_lines_02)-1):

                faces.extend(
                    bridgeLoops(
                        wall_lines_02[-(i+1)],
                        wall_lines_02[-(i+2)],
                        False))

    if centered:
        for v in verts:
            v[2]-=height/2

    return verts,edges,faces


def update_tube(self,context):

    if context.object is None:
        return

    mesh=context.object.data

    verts,edges,faces=primitive_Tube(
        self.radius_out,
        self.radius_in,
        self.height,
        self.use_inner,
        self.seg_perimeter,
        self.seg_radius,
        self.seg_height,
        self.sector_from,
        self.sector_to,
        self.centered,
        self.smoothed
    )

    mesh.clear_geometry()
    mesh.from_pydata(verts,edges,faces)

    if self.smoothed:
        for p in mesh.polygons:
            p.use_smooth=True

    mesh.update()


class WTubeData(bpy.types.PropertyGroup):

    radius_out: FloatProperty(name="Outer",default=1,min=0,update=update_tube)
    radius_in: FloatProperty(name="Inner",default=0,min=0,update=update_tube)
    height: FloatProperty(name="Height",default=2,min=0,update=update_tube)

    use_inner: BoolProperty(name="Use inner",default=True,update=update_tube)

    seg_perimeter: IntProperty(name="Perimeter",default=24,min=3,update=update_tube)
    seg_radius: IntProperty(name="Radius",default=1,min=1,update=update_tube)
    seg_height: IntProperty(name="Height",default=1,min=1,update=update_tube)

    sector_from: FloatProperty(name="From",default=0,min=0,max=2*pi,unit='ROTATION',update=update_tube)
    sector_to: FloatProperty(name="To",default=2*pi,min=0,max=2*pi,unit='ROTATION',update=update_tube)

    centered: BoolProperty(name="Centered",default=True,update=update_tube)
    smoothed: BoolProperty(name="Smooth",default=True,update=update_tube)


class Make_WTube(bpy.types.Operator):

    bl_idname="mesh.make_wtube"
    bl_label="WTube"
    bl_options={'UNDO','REGISTER'}

    def execute(self,context):

        verts,edges,faces=primitive_Tube(**WTube_Defaults)

        obj=create_mesh_object(context,verts,edges,faces,"WTube")
        mesh=obj.data

        mesh.WType='WTUBE'

        for k,v in WTube_Defaults.items():
            setattr(mesh.WTube,k,v)

        bpy.ops.object.shade_smooth()

        return{'FINISHED'}


def drawWTubePanel(self,context):

    layout=self.layout
    data=context.object.data.WTube

    layout.label(text="Type: WTube",icon='MESH_CYLINDER')

    row=layout.row()

    col=row.column(align=True)
    col.label(text="Radiuses")
    col.prop(data,"radius_out")
    col.prop(data,"radius_in")
    col.prop(data,"height")

    col=row.column(align=True)
    col.label(text="Segments")
    col.prop(data,"seg_perimeter")
    col.prop(data,"seg_radius")
    col.prop(data,"seg_height")

    col=row.column(align=True)
    col.label(text="Section")
    col.prop(data,"sector_from")
    col.prop(data,"sector_to")

    row=layout.row()
    row.prop(data,"use_inner")
    row.prop(data,"centered")
    row.prop(data,"smoothed")


def registerWTube():
    bpy.utils.register_class(Make_WTube)
    bpy.utils.register_class(WTubeData)
    bpy.types.Mesh.WTube = PointerProperty(type=WTubeData)


def unregisterWTube():
    bpy.utils.unregister_class(Make_WTube)
    bpy.utils.unregister_class(WTubeData)
    del bpy.types.Mesh.WTube
