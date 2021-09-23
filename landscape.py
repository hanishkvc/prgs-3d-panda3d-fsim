#!/usr/bin/env python3

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import GeoMipTerrain, PNMImage


class FSim(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        # Camera is the Main Actor for now
        self.dX = 0
        self.dY = 0.1
        self.dZ = 0
        self.gndWidth = 129
        self.gndHeight = 129
        self.create_terrain()
        self.camera.setPos(0, 0, 25)
        self.camera.setHpr(0, 0, 0)
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
            print("DBUG:Update:Camera:{}:Deltas:{}".format(self.camera.getPos(), [self.dX, self.dY, self.dZ]))
            self.terrain.update()
        x = self.camera.getX()+self.dX
        y = self.camera.getY()+self.dY
        z = self.camera.getZ()+self.dZ
        #print("DBUG:Update:", x, y, z)
        self.camera.setPos(x, y, z)
        return Task.cont


    def prepare(self):
        self.useDrive()
        self.taskMgr.add(self.update, 'UpdateFSim')


fsim = FSim()
fsim.prepare()
fsim.run()

