#!/usr/bin/env python3
# fsim - a simple flight simulator
# HanishKVC, 2021
# GPL
#

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import GeoMipTerrain, PNMImage, Vec3


class FSim(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        # Camera is the Main Actor for now
        self.cpos = Vec3(0, 0, 25)
        self.ctrans = Vec3(0, 0, 0)
        self.cface = Vec3(0, 0, 0)
        self.crot = Vec3(0, 0, 0)
        self.gndWidth = 129
        self.gndHeight = 129
        self.create_terrain()
        self.camera.setPos(self.cpos)
        self.camera.setHpr(self.cface)
        print("DBUG:Init:Camera:", self.camera.getPos())
        print("DBUG:Init:Camera:", self.camera.getPos())


    def create_terrain(self):
        self.terrain = GeoMipTerrain("Gnd")
        #self.terrain.setHeightField("./gnd_hf.png")
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
        # Color the terrain based on height
        cm = PNMImage(hf.getXSize(), hf.getYSize())
        print("DBUG:Terrain:CM:{}x{}".format(cm.getXSize(), cm.getYSize()))
        for x in range(hf.getXSize()):
            for y in range(hf.getYSize()):
                hfv = hf.getGray(x, y)
                if hfv < 0.25:
                    cm.setBlue(x, y, 1)
                elif hfv > 0.75:
                    cm.setRed(x, y, 1)
                else:
                    cm.setGreen(x, y, 1)
        self.terrain.setColorMap(cm)
        self.terrain.setBlockSize(32)
        self.terrain.setNear(10)
        self.terrain.setFar(50)
        self.terrain.setFocalPoint(self.camera)
        tRoot = self.terrain.getRoot()
        tRoot.setSz(100)
        tRoot.reparentTo(self.render)
        self.terrain.generate()


    def update(self, task):
        if (task.frame%24) == 0:
            print("DBUG:Update:240:Camera:{}:Trans:{}".format(self.camera.getPos(), self.ctrans))
            print("DBUG:Update:241:Camera:{}:Rotat:{}".format(self.camera.getPos(self.render), self.crot))
            self.terrain.update()
        self.cpos += self.ctrans
        self.camera.setPos(self.cpos)
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
            self.ctrans.x -= 0.01
        elif key == 'e':
            self.ctrans.x += 0.01


    def setup_keyshandler(self):
        self.accept("w", self.keys_handler, [ 'w' ])
        self.accept("s", self.keys_handler, [ 's' ])
        self.accept("q", self.keys_handler, [ 'q' ])
        self.accept("e", self.keys_handler, [ 'e' ])
        self.accept("a", self.keys_handler, [ 'a' ])
        self.accept("d", self.keys_handler, [ 'd' ])


    def prepare(self):
        #self.useDrive()
        self.setup_keyshandler()
        self.taskMgr.add(self.update, 'UpdateFSim')


fsim = FSim()
fsim.prepare()
fsim.run()

