#!/usr/bin/env python3
# fsim - a simple flight simulator
# HanishKVC, 2021
# GPL
#

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import GeoMipTerrain, PNMImage, Vec3
from panda3d.core import AmbientLight, DirectionalLight


class FSim(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        # Camera is the Main Actor for now
        self.cDefPos = Vec3(0, 0, 25)
        self.cDefFace = Vec3(0, 0, 0)
        self.ctrans = Vec3(0, 0, 0)
        self.crot = Vec3(0, 0, 0)
        self.gndWidth = 4097
        self.gndHeight = 4097
        #self.create_terrain("data/worldp1.png")
        self.create_terrain()
        self.camera.setPos(self.cDefPos)
        self.camera.setHpr(self.cDefFace)


    def setup_lights(self, bAmbient=False, bDirectional=True):
        if bAmbient:
            al = AmbientLight('AmbLight')
            al.setColor((0.5, 0.5, 0.5, 1))
            alnp = self.render.attachNewNode(al)
            self.render.setLight(alnp)
        if bDirectional:
            dl = DirectionalLight('DirLight')
            dl.setColor((0.9, 0.9, 0.8, 1))
            dlnp = self.render.attachNewNode(dl)
            dlnp.setHpr(0, -60, 0)
            self.render.setLight(dlnp)
            dl.setShadowCaster(True, 256, 256)
        self.render.setShaderAuto()


    def create_terrain(self, hfFile=None):
        self.terrain = GeoMipTerrain("Gnd")
        if hfFile == None:
            hf = PNMImage(self.gndWidth, self.gndHeight, PNMImage.CTGrayscale)
            print("DBUG:Terrain:HF:{}x{}".format(hf.getXSize(), hf.getYSize()))
            # Setup a height map
            for x in range(hf.getXSize()):
                for y in range(hf.getYSize()):
                    if x < hf.getXSize()/3:
                        hf.setGray(x, y, 0)
                    elif x < (hf.getXSize()*2/3):
                        hf.setGray(x, y, 0.5)
                    else:
                        hf.setGray(x, y, 1)
            self.terrain.setHeightfield(hf)
        else:
            self.terrain.setHeightfield(hfFile)
            hf = self.terrain.heightfield()
        # Color the terrain based on height
        cm = PNMImage(hf.getXSize(), hf.getYSize())
        print("DBUG:Terrain:CM:{}x{}".format(cm.getXSize(), cm.getYSize()))
        hfMin, hfMax = 256, 0
        for x in range(hf.getXSize()):
            for y in range(hf.getYSize()):
                hfv = hf.getGray(x, y)
                hfMin = min(hfMin, hfv)
                hfMax = max(hfMax, hfv)
                if hfv < 0.05:
                    cm.setBlue(x, y, 1)
                elif hfv > 0.75:
                    cm.setRed(x, y, 1)
                else:
                    cm.setGreen(x, y, 1)
        print("DBUG:Terrain:HFMinMax:{},{}".format(hfMin, hfMax))
        self.terrain.setColorMap(cm)
        self.terrain.setBlockSize(32)
        self.terrain.setNear(10)
        self.terrain.setFar(100)
        self.terrain.setFocalPoint(self.camera)
        tRoot = self.terrain.getRoot()
        tRoot.setSz(100)
        tRoot.reparentTo(self.render)
        self.terrain.generate()
        # Add some objects
        p = self.loader.loadModel("models/panda-model")
        p.setPos(50,100,0)
        p.setScale(0.01)
        p.reparentTo(self.render)


    def update(self, task):
        if (task.frame%4) == 0:
            self.terrain.update()
        if (task.frame%2400) == 0:
            print("DBUG:Update:{}:Camera:{}:Trans:{}:Rot:{}".format(task.frame, self.camera.getPos(), self.ctrans, self.crot))
        self.camera.setHpr(self.camera, self.crot)
        self.camera.setPos(self.camera, self.ctrans)
        return Task.cont


    def keys_handler(self, key):
        if key == 'a':
            self.ctrans.y += 0.01
        elif key == 'd':
            self.ctrans.y -= 0.01
        elif key == 'w':
            self.ctrans.z -= 0.01
        elif key == 's':
            self.ctrans.z += 0.01
        elif key == 'q':
            self.crot.x += 0.01
        elif key == 'e':
            self.crot.x -= 0.01
        elif key == 'z':
            self.ctrans.x -= 0.01
        elif key == 'c':
            self.ctrans.x += 0.01
        elif key == 'x':
            self.ctrans = Vec3(0,0,0)
            self.crot = Vec3(0,0,0)


    def setup_keyshandler(self):
        self.accept("w", self.keys_handler, [ 'w' ])
        self.accept("s", self.keys_handler, [ 's' ])
        self.accept("q", self.keys_handler, [ 'q' ])
        self.accept("e", self.keys_handler, [ 'e' ])
        self.accept("a", self.keys_handler, [ 'a' ])
        self.accept("d", self.keys_handler, [ 'd' ])
        self.accept("x", self.keys_handler, [ 'x' ])
        self.accept("z", self.keys_handler, [ 'z' ])
        self.accept("c", self.keys_handler, [ 'c' ])


    def prepare(self):
        self.disableMouse()
        #self.useDrive()
        self.setup_lights()
        self.setup_keyshandler()
        self.taskMgr.add(self.update, 'UpdateFSim')


fsim = FSim()
fsim.prepare()
fsim.run()

