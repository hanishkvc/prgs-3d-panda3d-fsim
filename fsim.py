#!/usr/bin/env python3
# fsim - a simple flight simulator
# HanishKVC, 2021
# GPL
#

import time
import sys

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import GeoMipTerrain, PNMImage, Vec3
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import TextNode


class FSim(ShowBase):

    def __init__(self, terrainFile=None, bTopView=True):
        ShowBase.__init__(self)
        # Camera is the Main Actor for now
        self.cDefPos = Vec3(0, 0, 25)
        self.cDefFace = Vec3(0, 0, 0)
        self.ctrans = Vec3(0, 0, 0)
        self.crot = Vec3(0, 0, 0)
        self.gndWidth = 4097
        self.gndHeight = 4097
        self.setup_texts()
        self.create_terrain(terrainFile)
        if bTopView:
            hf=self.terrain.heightfield()
            self.cDefPos = Vec3(hf.getXSize()/2, hf.getYSize()/2, hf.getXSize()*10)
            self.cDefFace = Vec3(0, -90, 0)
        self.camera.setPos(self.cDefPos)
        self.camera.setHpr(self.cDefFace)


    def setup_texts(self):
        # Cur State
        self.textPos = TextNode('TextPos')
        self.textPos.setText('Pos:')
        tpnp = self.render2d.attachNewNode(self.textPos)
        tpnp.setPos(-0.9, 0, 0.9)
        tpnp.setScale(0.04)
        self.textOr = TextNode('TextOr')
        self.textOr.setText('Orient:')
        tonp = self.render2d.attachNewNode(self.textOr)
        tonp.setPos(-0.9, 0, 0.8)
        tonp.setScale(0.04)
        # Change Actions
        self.textTrans = TextNode('TextTrans')
        self.textTrans.setText('Trans:')
        ttnp = self.render2d.attachNewNode(self.textTrans)
        ttnp.setPos(0.5, 0, 0.9)
        ttnp.setScale(0.04)
        self.textRot = TextNode('TextRot')
        self.textRot.setText('Rot:')
        trnp = self.render2d.attachNewNode(self.textRot)
        trnp.setPos(0.5, 0, 0.8)
        trnp.setScale(0.04)


    def setup_lights(self, bAmbient=True, bDirectional=True):
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
            #dl.setShadowCaster(True, 256, 256)
        self.render.setShaderAuto()


    def create_terrain(self, hfFile, bGrayShades=False, bNoBelowSeaLevel=True):
        """
        Terrain Auto Colormap based on heightfield could be
            With Below SeaLevel data (maybe)
                0.0 - 0.1 : SeaLevel and Below
                0.1 - 0.6 : ground and hills plus
                0.6 - 1.0 : Mountains etal
            No Below SeatLevel:
                0.0 - 0.0001 : Sea Level and Below
                0.0001 - 0.5 : Ground and Hills plus
                0.5   -  1.0 : Mountains etal
        """
        self.terrain = GeoMipTerrain("Gnd")
        if hfFile == None:
            hf = PNMImage(self.gndWidth, self.gndHeight, PNMImage.CTGrayscale)
            # Setup a height map
            for x in range(hf.getXSize()):
                for y in range(hf.getYSize()):
                    if x < hf.getXSize()/3:
                        hf.setGray(x, y, 0)
                    elif x < (hf.getXSize()*2/3):
                        hf.setGray(x, y, 0.5)
                    else:
                        hf.setGray(x, y, 1)
        else:
            hf = PNMImage(hfFile)
        print("DBUG:Terrain:HF:{}:{}x{}".format(hfFile, hf.getXSize(), hf.getYSize()))
        # Color the terrain based on height
        cm = PNMImage(hf.getXSize(), hf.getYSize())
        print("DBUG:Terrain:CM:{}x{}".format(cm.getXSize(), cm.getYSize()))
        hfMin, hfMax = 256, 0
        for x in range(hf.getXSize()):
            for y in range(hf.getYSize()):
                hfv = hf.getGray(x, y)
                hfMin = min(hfMin, hfv)
                hfMax = max(hfMax, hfv)
                if bGrayShades:
                    cm.setGray(x, y, hfv)
                else:
                    if bNoBelowSeaLevel:
                        if hfv < 0.0001:
                            cm.setBlue(x, y, (0.2+0.8*(hfv/0.0001)))
                        elif hfv < 0.25:
                            cm.setGreen(x, y, (0.2+0.8*(hfv/0.25)))
                        else:
                            cm.setRed(x, y, (0.2+0.8*((hfv-0.25)/0.75)))
                    else:
                        if hfv < 0.1:
                            cm.setBlue(x, y, (0.2+0.8*(hfv/0.1)))
                        elif hfv < 0.60:
                            cm.setGreen(x, y, (0.2+0.8*((hfv-0.1)/0.50)))
                        else:
                            cm.setRed(x, y, (0.2+0.8*((hfv-0.6)/0.40)))
        print("DBUG:Terrain:HFMinMax:{},{}".format(hfMin, hfMax))
        self.terrain.setHeightfield(hf)
        self.terrain.setColorMap(cm)
        blockSize = int((hf.getXSize()-1)/4)
        lodFar = blockSize/2
        lodNear = max(16,lodFar/32)
        print("DBUG:Terrain:LOD:BlockSize:{}:Far:{}:Near:{}".format(blockSize, lodFar, lodNear))
        self.terrain.setBlockSize(blockSize)
        self.terrain.setNear(lodNear)
        self.terrain.setFar(lodFar)
        self.terrain.setFocalPoint(self.camera)
        self.terrain.setAutoFlatten(GeoMipTerrain.AFMStrong)
        self.terrain.setBruteforce(True)
        tRoot = self.terrain.getRoot()
        tRoot.setSx(4)
        tRoot.setSy(4)
        tRoot.setSz(400)
        tRoot.reparentTo(self.render)
        self.terrain.generate()
        # Add some objects
        p = self.loader.loadModel("models/panda-model")
        p.setPos(50,100,0)
        p.setScale(0.01)
        p.reparentTo(self.render)
        print("DBUG:Terrain:AfterScale:{}x{}".format(self.terrain.heightfield().getXSize(), self.terrain.heightfield().getYSize()))


    def update(self, task):
        cGP = self.camera.getPos()
        cOr = self.camera.getHpr()
        cTr = self.ctrans
        cRo = self.crot
        if (task.frame%4) == 0:
            self.terrain.update()
            self.textPos.setText("P:{:6.2f},{:6.2f},{:6.2f}".format(cGP[0], cGP[1], cGP[2]))
            self.textOr.setText("O:{:6.2f},{:6.2f},{:6.2f}".format(cOr[0], cOr[1], cOr[2]))
            self.textTrans.setText("T:{:6.2f},{:6.2f},{:6.2f}".format(cTr[0], cTr[1], cTr[2]))
            self.textRot.setText("R:{:6.2f},{:6.2f},{:6.2f}".format(cRo[0], cRo[1], cRo[2]))
        if (task.frame%2400) == 0:
            curT = time.time()
            fps = 2400/(curT - self.updateT1)
            self.updateT1 = curT
            print("DBUG:Update:{}:FPS{:5.2f}:Camera:{}:Trans:{}:Rot:{}".format(task.frame, fps, self.camera.getPos(), self.ctrans, self.crot))
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
        elif key == 'r':
            self.crot.y += 0.01
        elif key == 'f':
            self.crot.y -= 0.01
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
        self.accept("r", self.keys_handler, [ 'r' ])
        self.accept("f", self.keys_handler, [ 'f' ])


    def prepare(self):
        self.disableMouse()
        #self.useDrive()
        self.setup_lights()
        self.setup_keyshandler()
        self.updateT1 = time.time()
        self.taskMgr.add(self.update, 'UpdateFSim')


def handle_args(args):
    global terrainFile, bTopView
    iArg = 0
    while iArg < (len(args)-1):
        iArg += 1
        cArg = args[iArg]
        if cArg == "--terrain":
            iArg += 1
            terrainFile = args[iArg]
        if cArg == "--topview":
            bTopView = True



terrainFile=None
bTopView=False
handle_args(sys.argv)
fsim = FSim(terrainFile, bTopView)
fsim.prepare()
fsim.run()

