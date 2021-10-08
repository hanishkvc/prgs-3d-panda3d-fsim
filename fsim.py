#!/usr/bin/env python3
# fsim - a simple flight simulator
# HanishKVC, 2021
# GPL
#

import time
import sys, os

import numpy
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import GeoMipTerrain, PNMImage, Vec3
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import TextNode, NodePath


class FSim(ShowBase):

    def __init__(self, cfg):
        ShowBase.__init__(self)
        self.cfg = cfg
        self.prevFrameTime = 0.0
        self.frameCnt = 0
        # Camera is the Main Actor for now
        self.cDefPos = Vec3(0, 0, 25)
        self.cDefFace = Vec3(0, 0, 0)
        self.ctrans = Vec3(0, 0, 0)
        self.crot = Vec3(0, 0, 0)
        self.gndWidth = 4097
        self.gndHeight = 4097
        self.setup_mc()
        self.setup_texts()
        self.create_terrain(cfg['sTerrainFile'])
        hf=self.terrain.heightfield()
        if cfg['bTopView']:
            self.cDefPos = Vec3(hf.getXSize()/2, hf.getYSize()/2, hf.getXSize()*10)
            self.cDefFace = Vec3(0, -90, 0)
        self.set_mcc(self.cDefPos, self.cDefFace)
        self.updateCPos = self.camera.getPos()
        self.updateDelta = numpy.average((hf.getXSize(), hf.getYSize()))*0.07


    def setup_mc(self):
        #self.mc = NodePath()
        #self.mc.reparentTo(self.render)
        self.mc = self.render.attachNewNode("MC")


    def set_mcc(self, pos, hpr):
        self.mc.setPos(pos)
        self.mc.setHpr(hpr)
        self.camera.setPos(pos)
        self.camera.setHpr(hpr)


    def setup_texts(self):
        # Status line
        self.textStatus = TextNode('TextStatus')
        self.textStatus.setText('Status:')
        tsnp = self.render2d.attachNewNode(self.textStatus)
        tsnp.setPos(-0.2, 0, 0.9)
        tsnp.setScale(0.04)
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
        ttnp.setPos(0.2, 0, 0.9)
        ttnp.setScale(0.04)
        self.textRot = TextNode('TextRot')
        self.textRot.setText('Rot:')
        trnp = self.render2d.attachNewNode(self.textRot)
        trnp.setPos(0.2, 0, 0.8)
        trnp.setScale(0.04)
        fwFont = loader.loadFont("cmtt12.egg")
        for t in [ self.textPos, self.textOr, self.textTrans, self.textRot, self.textStatus ]:
            t.setFont(fwFont)
            #t.setShadow(0.05,0.05)
            #t.setShadowColor(0.2,0.2,0.2,1.0)
            t.setCardColor(0.2,0.2,0.2,1.0)
            t.setCardAsMargin(0.2,0.2,0.2,0.2)
            t.setCardDecal(True)


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


    def _create_heightfield(self):
        hf = PNMImage(self.gndWidth, self.gndHeight, PNMImage.CTGrayscale)
        # Setup a height map
        for x in range(hf.getXSize()):
            for y in range(hf.getYSize()):
                if x < hf.getXSize()/3:
                    hf.setGray(x, y, 0)
                elif x < (hf.getXSize()*2/3):
                    hf.setGray(x, y, 0.22)
                else:
                    hf.setGray(x, y, 1)
        return hf


    def _create_colormap(self, hf):
        cm = PNMImage(hf.getXSize(), hf.getYSize())
        print("DBUG:Terrain:CM:{}x{}".format(cm.getXSize(), cm.getYSize()))
        hfMin, hfMax = 256, 0
        for x in range(hf.getXSize()):
            for y in range(hf.getYSize()):
                hfv = hf.getGray(x, y)
                hfMin = min(hfMin, hfv)
                hfMax = max(hfMax, hfv)
                if self.cfg['bCMGrayShades']:
                    cm.setXel(x, y, hfv)
                else:
                    if self.cfg['bHFNoBelowSeaLevel']:
                        if hfv < 0.000001:
                            cm.setBlue(x, y, (0.2+0.8*(hfv/0.000001)))
                        elif hfv < 0.25:
                            cm.setGreen(x, y, (0.2+0.8*(hfv/0.25)))
                        elif hfv < 0.75:
                            cm.setRed(x, y, (0.2+0.8*((hfv-0.25)/0.50)))
                        else:
                            cm.setXel(x, y, (0.2+0.8*((hfv-0.75)/0.25)))
                    else:
                        if hfv < 0.1:
                            cm.setBlue(x, y, (0.2+0.8*(hfv/0.1)))
                        elif hfv < 0.60:
                            cm.setGreen(x, y, (0.2+0.8*((hfv-0.1)/0.50)))
                        else:
                            cm.setRed(x, y, (0.2+0.8*((hfv-0.6)/0.40)))
        print("DBUG:Terrain:CM:HFMinMax:{},{}".format(hfMin, hfMax))
        return cm


    def create_terrain(self, hfFile, bCMGrayShades=False, bHFNoBelowSeaLevel=True):
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
        self.cfg['bCMGrayShades'] = bCMGrayShades
        self.cfg['bHFNoBelowSeaLevel'] = bHFNoBelowSeaLevel
        self.terrain = GeoMipTerrain("Gnd")
        self.terrain.setMinLevel(self.cfg['LODMinLevel'])
        # The Heightfield
        cmFName = None
        cmFNameSave = None
        if hfFile == None:
            hf = self._create_heightfield()
        else:
            hfFName = "{}.hf.png".format(hfFile)
            cmFName = "{}.cm.png".format(hfFile)
            if not os.path.exists(cmFName):
                cmFNameSave = cmFName
                cmFName = None
            hf = PNMImage(hfFName)
        print("DBUG:Terrain:HF:{}:{}x{}".format(hfFile, hf.getXSize(), hf.getYSize()))
        # Color the terrain based on height
        if cmFName == None:
            cm = self._create_colormap(hf)
        else:
            cm = PNMImage(cmFName)
        if cmFNameSave != None:
            cm.write(cmFNameSave)
        self.terrain.setHeightfield(hf)
        self.terrain.setColorMap(cm)
        blockSize = int((hf.getXSize()-1)/8)
        lodFar = blockSize*2
        lodNear = max(64,lodFar/4)
        #blockSize = 1024
        #lodFar = 2048
        #lodNear = 512
        print("DBUG:Terrain:LOD:BlockSize:{}:Far:{}:Near:{}".format(blockSize, lodFar, lodNear))
        self.terrain.setBlockSize(blockSize)
        self.terrain.setNear(lodNear)
        self.terrain.setFar(lodFar)
        self.terrain.setFocalPoint(self.camera)
        self.terrain.setAutoFlatten(self.cfg['LODAFMode'])
        self.terrain.setBruteforce(self.cfg['bLODBruteForce'])
        tRoot = self.terrain.getRoot()
        #tRoot.setSx(4)
        #tRoot.setSy(4)
        tRoot.setSz(200)
        tRoot.reparentTo(self.render)
        self.terrain.generate()
        # Add some objects
        p = self.loader.loadModel("models/panda-model")
        p.setPos(50,100,0)
        p.setScale(0.01)
        p.reparentTo(self.render)
        print("DBUG:Terrain:AfterScale:{}x{}".format(self.terrain.heightfield().getXSize(), self.terrain.heightfield().getYSize()))


    def update_instruments_text(self, cPo, cOr, cTr, cRo):
        self.textPos.setText("P:{:08.2f},{:08.2f},{:08.2f}".format(cPo[0], cPo[1], cPo[2]))
        self.textOr.setText("O:{:08.2f},{:08.2f},{:08.2f}".format(cOr[0], cOr[1], cOr[2]))
        self.textTrans.setText("T:{:08.4f},{:08.4f},{:08.4f}".format(cTr[0], cTr[1], cTr[2]))
        self.textRot.setText("R:{:08.4f},{:08.4f},{:08.4f}".format(cRo[0], cRo[1], cRo[2]))


    def update(self, task):
        timeDelta = task.time - self.prevFrameTime
        timeDelta = timeDelta/0.04
        if timeDelta < 1:
            return Task.cont
        self.prevFrameTime = task.time
        self.frameCnt += 1
        cPo = self.camera.getPos()
        cOr = self.camera.getHpr()
        cTr = self.ctrans
        cRo = self.crot
        # Update terrain or not
        updateDelta = (self.updateCPos - cPo).length()
        self.textStatus.setText("NU:{:05.2f}".format(updateDelta))
        if (updateDelta > self.updateDelta):
            self.terrain.update()
            self.updateCPos = cPo
        # Update instruments
        if (self.frameCnt%4) == 0:
            self.update_instruments_text(cPo, cOr, cTr, cRo)
        # Update log
        if (self.frameCnt%2400) == 0:
            curT = time.time()
            fps = 2400/(curT - self.updateT1)
            self.updateT1 = curT
            print("DBUG:Update:{}:FPS{:5.2f}:Camera:{}:Trans:{}:Rot:{}".format(task.frame, fps, self.camera.getPos(), self.ctrans, self.crot))
        # Update MainChar the plane
        self.update_mc()
        return Task.cont


    def update_mc_ss(self):
        self.camera.setHpr(self.camera, self.crot)
        self.camera.setPos(self.camera, self.ctrans)


    def ss_keys_handler(self, key):
        """
        Handle keys to simulate a spaceship
        """
        if key == 'a':
            self.ctrans.x -= 0.01
        elif key == 'd':
            self.ctrans.x += 0.01
        elif key == 'w':
            self.ctrans.y += 0.01
        elif key == 's':
            self.ctrans.y -= 0.01
        elif key == 'q':
            self.ctrans.z += 0.01
        elif key == 'e':
            self.ctrans.z -= 0.01
        elif key == 'j':
            self.crot.x += 0.01
        elif key == 'l':
            self.crot.x -= 0.01
        elif key == 'i':
            self.crot.y -= 0.01
        elif key == 'k':
            self.crot.y += 0.01
        elif key == 'u':
            self.crot.z -= 0.01
        elif key == 'o':
            self.crot.z += 0.01
        elif key == 'x':
            self.ctrans = Vec3(0,0,0)
            self.crot = Vec3(0,0,0)


    def setup_ss_keyshandler(self):
        for k in [ "w", "s", "q", "e", "a", "d", "x", "i", "k", "j", "l", "u", "o" ]:
            self.accept("{}-repeat".format(k), self.ss_keys_handler, [ k ])
        for k in [ "w", "s", "q", "e", "a", "d", "x", "i", "k", "j", "l", "u", "o" ]:
            self.accept(k, self.ss_keys_handler, [ k ])


    def update_mc_ac(self):
        self.camera.setHpr(self.camera, self.crot)
        self.camera.setPos(self.camera, self.ctrans)


    def ac_keys_handler(self, key):
        """
        Handle keys to simulate a aircraft
        """
        if key == 'a':
            self.ctrans.y += 0.01
        elif key == 'd':
            self.ctrans.y -= 0.01
        elif key == 'w':
            self.crot.y -= 0.01
        elif key == 's':
            self.crot.y += 0.01
        elif key == 'q':
            self.crot.x += 0.01
        elif key == 'e':
            self.crot.x -= 0.01
        elif key == 'x':
            self.ctrans = Vec3(0,0,0)
            self.crot = Vec3(0,0,0)


    def setup_ac_keyshandler(self):
        self.accept("w", self.ac_keys_handler, [ 'w' ])
        self.accept("s", self.ac_keys_handler, [ 's' ])
        self.accept("q", self.ac_keys_handler, [ 'q' ])
        self.accept("e", self.ac_keys_handler, [ 'e' ])
        self.accept("a", self.ac_keys_handler, [ 'a' ])
        self.accept("d", self.ac_keys_handler, [ 'd' ])
        self.accept("x", self.ac_keys_handler, [ 'x' ])


    def prepare(self):
        if self.cfg['bP3DCameraControl']:
            self.useDrive()
        else:
            self.disableMouse()
        self.setup_lights()
        if self.cfg['bModeAC']:
            self.setup_ac_keyshandler()
            self.update_mc = self.update_mc_ac
        else:
            self.setup_ss_keyshandler()
            self.update_mc = self.update_mc_ss
        self.updateT1 = time.time()
        self.taskMgr.add(self.update, 'UpdateFSim')


def handle_args(args):
    cfg = {
        'sTerrainFile': None,
        'bModeAC': False,
        'bTopView': False,
        'bLODBruteForce': False,
        'bP3DCameraControl': False,
        'LODAFMode': GeoMipTerrain.AFMOff,
        'LODMinLevel': 0,
        }
    iArg = 0
    while iArg < (len(args)-1):
        iArg += 1
        cArg = args[iArg]
        if cArg == "--sTerrainFile":
            iArg += 1
            cfg['sTerrainFile'] = args[iArg]
        elif cArg.startswith("--b"):
            k = cArg[2:]
            iArg += 1
            v = args[iArg]
            if v.lower() in [ "false", "no", "beda", "venda", "nahi" ]:
                v = False
            else:
                v = True
            cfg[k] = v
        elif cArg == "--LODAFMode":
            iArg += 1
            afMode = args[iArg].lower()
            if afMode == "light":
                cfg['LODAFMode'] = GeoMipTerrain.AFMLight
            elif afMode == "medium":
                cfg['LODAFMode'] = GeoMipTerrain.AFMMedium
            elif afMode == "strong":
                cfg['LODAFMode'] = GeoMipTerrain.AFMStrong
            else:
                cfg['LODAFMode'] = GeoMipTerrain.AFMOff
        elif cArg == "--LODMinLevel":
            iArg += 1
            cfg['LODMinLevel'] = int(args[iArg])
        elif cArg == "--help":
            print(cfg)
            exit()
    print("INFO:Args:",cfg)
    return cfg


cfg = handle_args(sys.argv)
fsim = FSim(cfg)
fsim.prepare()
fsim.run()

