#___________________________________/
#___Author:_________Vit_Prochazka___/
#___Created:________14.08.2017______/
#___Last_modified:__14.08.2017______/
#___Version:________0.2_____________/
#___________________________________/

from mathutils import Vector
from math import sqrt

def baseHedron(base):

    verts = []
    edges = []
    faces = []

    if base == "CUBE":
        verts = [
            Vector((-1,-1,-1)),
            Vector((1,-1,-1)),
            Vector((1,1,-1)),
            Vector((-1,1,-1)),
            Vector((-1,-1,1)),
            Vector((1,-1,1)),
            Vector((1,1,1)),
            Vector((-1,1,1))
        ]
        faces = [
            (3,2,1,0),
            (0,1,5,4),
            (1,2,6,5),
            (2,3,7,6),
            (3,0,4,7),
            (4,5,6,7)
        ]

    elif base == "TETRA":
        a = 1/sqrt(2)
        verts = [
            Vector((1,0,-a)),
            Vector((-1,0,-a)),
            Vector((0,1,a)),
            Vector((0,-1,a))
        ]
        faces = [
            (0,3,1),
            (0,2,3),
            (0,1,2),
            (1,3,2)
        ]

    elif base == "OCTA":
        verts = [
            Vector((1,0,0)),
            Vector((-1,0,0)),
            Vector((0,1,0)),
            Vector((0,-1,0)),
            Vector((0,0,1)),
            Vector((0,0,-1))
        ]
        faces = [
            (0,3,5),
            (0,5,2),
            (1,2,5),
            (1,5,3),
            (0,4,3),
            (0,2,4),
            (1,4,2),
            (1,3,4)
        ]

    elif base == "ICOSA":
        a = (1+sqrt(5))/2
        verts = [
            Vector((0,1,a)),
            Vector((0,1,-a)),
            Vector((0,-1,a)),
            Vector((0,-1,-a)),

            Vector((1,a,0)),
            Vector((1,-a,0)),
            Vector((-1,a,0)),
            Vector((-1,-a,0)),

            Vector((a,0,1)),
            Vector((a,0,-1)),
            Vector((-a,0,1)),
            Vector((-a,0,-1)),
        ]
        faces = [
            (0,8,4),
            (0,4,6),
            (0,6,10),
            (0,10,2),
            (0,2,8),
            (4,8,9),
            (1,4,9),
            (1,6,4),
            (1,11,6),
            (6,11,10),
            (7,10,11),
            (2,10,7),
            (5,2,7),
            (2,5,8),
            (5,9,8),
            (3,9,5),
            (1,9,3),
            (1,3,11),
            (3,7,11),
            (3,5,7)
        ]

    return verts, edges, faces
