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

    def add_triangle(self, vi0, vi1, vi2):
        self.prim.addVertices(vi0, vi1, vi2)
        self.prim.closePrimitive()

    def add_triangles(self, va):
        for v in va:
            self.add_triangle(v[0], v[1], v[2])

    def generate(self):
        self.geom = Geom(self.vdata)
        self.geom.addPrimitive(self.prim)
        self.geomNode = GeomNode(self.name)
        self.geomNode.addGeom(self.geom)
        return self.geomNode

