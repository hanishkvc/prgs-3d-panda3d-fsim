# A bunch of Panda3D primitives
# HanishKVC, 2021
# GPL

from panda3d.core import GeomVertexFormat
from panda3d.core import GeomVertexData, Geom, GeomVertexWriter
from panda3d.core import GeomTriangles, GeomNode

class Polyhedron():

    def __init__(self, name, numVertices=None):
        self.name = name
        self.gvf = GeomVertexFormat.get_v3t2()
        self.vdata = GeomVertexData(name, self.gvf, Geom.UHStatic)
        if numVertices != None:
            self.vdata.setNumRows(numVertices)
        self.gvwVertex = GeomVertexWriter(self.vdata, 'vertex')
        self.gvwTexCo = GeomVertexWriter(self.vdata, 'texcoord')
        self.prim = GeomTriangles(Geom.UHStatic)

    def add_vertex(self, xyz, uv=None):
        if uv == None:
            uv = (xyz[0], xyz[1])
        self.gvwVertex.addData3(xyz)
        self.gvwTexCo.addData2(uv)

    def add_vertices(self, va):
        for v in va:
            self.add_vertex(v)

    def add_triangle(self, vi0, vi1, vi2):
        self.prim.addVertices(vi0, vi1, vi2)
        self.prim.closePrimitive()

    def add_triangles(self, ta):
        for t in ta:
            self.add_triangle(t[0], t[1], t[2])

    def generate(self):
        self.geom = Geom(self.vdata)
        self.geom.addPrimitive(self.prim)
        self.geomNode = GeomNode(self.name)
        self.geomNode.addGeom(self.geom)
        return self.geomNode


def create_cube(name):
    m1 = Polyhedron(name)
    # Vertices array
    va = [ (0,0,0),
           (0,1,0),
           (1,1,0),
           (1,0,0),
           (0,0,1),
           (0,1,1),
           (1,1,1),
           (1,0,1) ]
    m1.add_vertices(va)
    # Triangle Faces array
    ta = [ [0,2,1], [0,3,2],
           [4,6,5], [4,7,6],
           [0,4,5], [0,5,1],
           [3,7,6], [3,6,2],
           [0,3,7], [0,7,4],
           [1,2,6], [1,6,5] ]
    m1.add_triangles(ta)
    m1gn = m1.generate()
    return m1gn


