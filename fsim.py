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
from panda3d.core import TextNode, NodePath, CardMaker, TextFont
from direct.gui.OnscreenText import OnscreenText
from direct.stdpy import threading

import p3dprims as pp


VERSION='v20211013IST1703'


class FSim(ShowBase):

    def __init__(self, cfg):
        ShowBase.__init__(self)
        self.cfg = cfg
        # Init some defaults
        self.prevFrameTime = 0.0
        self.frameCnt = 0
        self.cDefPos = Vec3(0, 0, 25)
        self.cDefFace = Vec3(0, 0, 0)
        self.ctrans = Vec3(0, 0, 0)
        self.crot = Vec3(0, 0, 0)
        self.gndWidth = 4097
        self.gndHeight = 4097
        # Setup the world
        self.setup_mc()
        self.setup_hud()
        self.create_terrain(cfg['sTerrainFile'])
        self.create_objects(cfg['sTerrainFile'])
        self.init_with_world()


    def init_with_world(self):
        """
        Adjust things based on loaded terrain and initialise.
        """
        hf=self.terrain.heightfield()
        if cfg['bTopView']:
            self.cDefPos = Vec3(hf.getXSize()/2, hf.getYSize()/2, hf.getXSize()*10)
            self.cDefFace = Vec3(0, -90, 0)
        self.uoPos = Vec3(self.cDefPos)
        self.set_mcc(self.cDefPos, self.cDefFace)
        self.updateCPos = self.camera.getPos()
        self.updateDelta = numpy.average((hf.getXSize(), hf.getYSize()))*0.05


    def setup_mc(self):
        """
        Skeleton for the helper which will load/create the main character ie the plane.
        Camera is the Main Actor for now
        """
        #self.mc = NodePath()
        #self.mc.reparentTo(self.render)
        self.mc = self.render.attachNewNode("MC")


    def set_mcc(self, pos, hpr):
        """
        Skeleton of a helper for when there will be a plane model beyond the lone camera,
        i.e to represent the plane/user/main-character.
        Based on current plane position, one will have to adjust the camera according
        to the view selected by user like 1st person or 3rd person or rotate or ...
        """
        self.mc.setPos(pos)
        self.mc.setHpr(hpr)
        self.camera.setPos(pos)
        self.camera.setHpr(hpr)


    def setup_hud(self):
        """
        Setup the instrument cluster, which shows
            current position and orientation,
            translation and rotation actions that are being applied,
            the height above ground,
            distance moved relative to last world update.
        """
        self.hud = {}
        self.hud['frame'] = CardMaker("HUD")
        self.hud['frame'].setColor(0.1,0.2,0.1,0.2)
        self.hud['frame'].setFrame(-0.94,0.94,0.74,0.98)
        self.hud['frameNP'] = self.render2d.attachNewNode(self.hud['frame'].generate())
        self.hud['frameNP'].setTransparency(True)
        fwFont = loader.loadFont("cmtt12.egg")
        lO = [
                # Cur State
                [ "Pos", (-0.9, 0.9), 0.04 ],
                [ "Ori", (-0.9, 0.8), 0.04 ],
                # Change Actions
                [ "Tra", ( 0.3, 0.9), 0.04 ],
                [ "Rot", ( 0.3, 0.8), 0.04 ],
                # Status
                [ "S1",  (-0.1, 0.9), 0.04 ],
                [ "S2",  (-0.1, 0.8), 0.04 ],
            ]
        for o in lO:
            self.hud[o[0]] = TextNode(o[0])
            np = self.hud['frameNP'].attachNewNode(self.hud[o[0]])
            np.setPos(o[1][0], 1, o[1][1])
            np.setScale(o[2])
            self.hud[o[0]].setText(o[0])
            self.hud[o[0]].setFont(fwFont)
            #self.hud[o[0]].setShadow(0.05,0.05)
            #self.hud[o[0]].setShadowColor(0.2,0.2,0.2,1.0)
            self.hud[o[0]].setCardColor(0.2,0.2,0.2,1.0)
            self.hud[o[0]].setCardAsMargin(0.2,0.2,0.2,0.2)
            self.hud[o[0]].setCardDecal(True)


    def setup_lights(self, bAmbient=True, bDirectional=True):
        """
        Setup a ambient as well as a direction light.
        """
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
        """
        If user doesnt specify any terrain, then generate a simple terrain.
        """
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
        """
        Color the passed terrain based on height.
            With Below SeaLevel data (maybe)
                0.0 - 0.1 : SeaLevel and Below
                0.1 - 0.6 : ground and hills plus
                0.6 - 1.0 : Mountains etal
            No Below SeatLevel:
                0.0 - 0.0001 : Sea Level and Below
                0.0001 - 0.5 : Ground and Hills plus
                0.5   -  1.0 : Mountains etal
        """
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
        Create a terrain based on the passed heightfield and colormap.
        """
        self.cfg['bCMGrayShades'] = bCMGrayShades
        self.cfg['bHFNoBelowSeaLevel'] = bHFNoBelowSeaLevel
        self.terrain = GeoMipTerrain("Gnd")
        self.terrain.setMinLevel(self.cfg['iLODMinLevel'])
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
            self.gndWidth, self.gndHeight = hf.getXSize(), hf.getYSize()
        print("DBUG:Terrain:HF:{}:{}x{}".format(hfFile, hf.getXSize(), hf.getYSize()))
        # Colormap for the terrain
        if cmFName == None:
            cm = self._create_colormap(hf)
        else:
            cm = PNMImage(cmFName)
        if cmFNameSave != None:
            cm.write(cmFNameSave)
        self.terrain.setHeightfield(hf)
        self.terrain.setColorMap(cm)
        blockSize = int((hf.getXSize()-1)/8)
        lodFar = blockSize*4
        lodNear = max(64,lodFar/4)
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
        tRoot.setSz(100)
        tRoot.reparentTo(self.render)
        self.terrain.generate()
        print("DBUG:Terrain:AfterScale:{}x{}".format(self.terrain.heightfield().getXSize(), self.terrain.heightfield().getYSize()))
        # Add some objects
        p = self.loader.loadModel("models/panda-model")
        p.setPos(50,100,0)
        p.setScale(0.01)
        p.reparentTo(self.render)


    def create_objects(self, baseFName, bFont3D=False):
        """
        Create objects corresponding to the entries in the objects file.
        For now it creates a floating cube with its name, wrt each entry.
        """
        objsFName = "{}.objects".format(baseFName)
        try:
            f = open(objsFName)
        except:
            print("WARN:CreateObjects:Returning empty handed")
            return
        if bFont3D:
            ttfFont = loader.loadFont("data/comic.ttf", color = (1,1,1,1), renderMode = TextFont.RMSolid)
        hf=self.terrain.heightfield()
        hdr1 = f.readline()
        hdr2 = f.readline()
        if not hdr2.startswith("HDR2:"):
            raise RuntimeError("ERRR:CreateObjects:Invalid Objects file:{}".format(objsFName))
        hdr2 = hdr2.split(":")
        oXW,oYH = int(hdr2[2]), int(hdr2[4])
        cXW = hf.getXSize()
        cYH = hf.getYSize()
        xMult = cXW/oXW
        yMult = cYH/oYH
        print("INFO:CreateObjects:Adj:{}x{}:{}x{}:{}x{}".format(oXW, oYH, cXW, cYH, xMult, yMult))
        self.objsDistThreshold = int(max(cXW, cYH)/4)**2
        self.modelPaths = {}
        self.objs = {}
        self.objsNPA = numpy.zeros(1024*3).reshape(1024,3)
        self.objsCnt = -1
        alreadyIn = set()
        for l in f:
            la = l.strip()
            la = la[1:-1].split(',')
            if la[0].strip().upper() == "MODELPATH":
                self.modelPaths[la[1].strip()] = la[2].strip()
                continue
            x = int(la[0])
            aX = int(x*xMult)
            y = int(la[1])
            aY = int(y*yMult)
            aY = self.y_interchange(aY)
            self.update_xyheight_img(x, aY)
            aZ = self.terrainXYHeight+10
            name = la[2].strip()[1:-1]
            if name in alreadyIn:
                continue
            self.objsCnt += 1
            alreadyIn.add(name)
            if len(la) > 3:
                model = la[3].strip()
            else:
                model = ''
            print("INFO:CreateObjects:{:4}:{:6}:{:4}x{:4}:{:4}x{:4}:{}".format(self.objsCnt, model, x, y, aX, aY, name))
            if model == '':
                m1 = pp.create_cube("{}".format(self.objsCnt))
                m1np = self.render.attachNewNode(m1)
            else:
                m1np = loader.loadModel(self.modelPaths[model])
                m1np.reparentTo(self.render)
            m1np.setPos(aX, aY, aZ)
            m1np.setScale(4)
            m1np.hide()
            if model == '':
                txt = OnscreenText(text=name)
                txtn = txt.node()
                if bFont3D:
                    txtn.setFont(ttfFont)
                txtnp = self.render.attachNewNode(txtn)
                txtnp.setPos(aX+2, aY-1, aZ+1)
                txtnp.setScale(10)
                txtnp.hide()
            else:
                txtnp = None
            self.objs[self.objsCnt] = { 'm': m1np, 't': txtnp, 'n': name }
            self.objsNPA[self.objsCnt] = [aX, aY, aZ]


    def update_objects(self):
        """
        Based on distance wrt current plane position, decide whether to show a object or not.
        NOTE: It doesnt worry about z axis(ie height).
        """
        tX = self.objsNPA[:,0] - self.uoPos.x
        tY = self.objsNPA[:,1] - self.uoPos.y
        d = tX**2 + tY**2
        l = numpy.argwhere(d < self.objsDistThreshold)
        print("INFO:UpdateObjects:", self.uoPos, self.objsDistThreshold, l[l < self.objsCnt])
        for i in range(self.objsCnt):
            if i in l:
                self.objs[i]['m'].show()
                if self.objs[i]['t'] != None:
                    self.objs[i]['t'].show()
                print(self.objs[i]['n'], d[i])
            else:
                self.objs[i]['m'].hide()
                if self.objs[i]['t'] != None:
                    self.objs[i]['t'].hide()


    def update_world_tf(self):
        """
        The thread function, which triggers the objects and terrain update logics within it.
        """
        self.update_objects()
        self.terrain.update()


    def update_instruments_text(self, cPo, cOr, cTr, cRo):
        """
        Update the instrument cluster in the HUD.
        Also trigger a shaking of the HUD, if the speed along any axis is very large.
        """
        if (max(cTr) > 2):
            r = numpy.random.random(2)
            self.hud['frameNP'].setPos(0-r[0]*0.01, 0, 0-r[1]*0.02)
        self.hud['Pos'].setText("P:{:08.2f},{:08.2f},{:08.2f}".format(cPo[0], cPo[1], cPo[2]))
        self.hud['Ori'].setText("O:{:08.2f},{:08.2f},{:08.2f}".format(cOr[0], cOr[1], cOr[2]))
        self.hud['Tra'].setText("T:{:08.4f},{:08.4f},{:08.4f}".format(cTr[0], cTr[1], cTr[2]))
        self.hud['Rot'].setText("R:{:08.4f},{:08.4f},{:08.4f}".format(cRo[0], cRo[1], cRo[2]))


    def y_interchange(self, y):
        """
        Switch y between 3d and Image Co-Ords
        """
        hf=self.terrain.heightfield()
        return hf.getYSize() - y - 1


    def update_xyheight_3d(self, x, y):
        """
        Get the height of the ground/terrain wrt the passed x,y location in 3d world.
        NOTE: The found value is stored into a internal variable.
        """
        y = self.y_interchange(y)
        self.update_xyheight_img(x, y)


    def update_xyheight_img(self, x, y):
        """
        Get the height of the ground/terrain wrt the passed x,y location in texture/colormap/image space.
        NOTE: The found value is stored into a internal variable.
        """
        hf=self.terrain.heightfield()
        self.terrainXYHeight = hf.getGray(x, y)*self.terrain.getRoot().getSz()


    def update_terrain_height(self, cPos):
        """
        Get and update the height of the terrain, at current location (cPos) in the hud.
        """
        try:
            self.update_xyheight_3d(int(cPos.x), int(cPos.y))
            self.hud['S2'].setText("H:{:06.3f}".format(self.terrainXYHeight/10))
        except:
            if self.cfg['bDebug']:
                print(sys.exc_info())
            self.terrainXYHeight = -999
            if self.cfg['bModeAC']:
                crot = Vec3(-180, 0, 0)
                self.camera.setHpr(self.camera, crot)


    def update_world(self, cPos):
        """
        The helper which calls the thread for updating the world.
        """
        self.uoPos.x = cPos.x
        self.uoPos.y = cPos.y
        self.uoPos.z = cPos.z
        self.threadUpdate.run()


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
        # Update World or not
        updateDelta = (self.updateCPos - cPo).length()
        if (updateDelta > self.updateDelta):
            self.update_world(cPo)
            self.updateCPos = cPo
        # Update instruments
        if (self.frameCnt%4) == 0:
            self.hud['S1'].setText("NU:{:05.2f}".format(updateDelta))
            self.update_terrain_height(cPo)
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
        """
        Update the plane in Spaceship mode.
        """
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
        """
        Simulate a simple aircraft flying logic.
        Lift is affected by
            Speed, Height, Angle
        """
        cPo = self.camera.getPos()
        cOr = self.camera.getHpr()
        d = self.ctrans.y - self.mcMinAccel4PLift
        if d > 0:
            lift = d/8.0
            heightEffect = (1-cPo.z/self.mcMaxHeight)
            lift *= heightEffect
        else:
            lift = d/32.0
        aAdj = cOr.y/self.mcMaxAngle4PLift
        if aAdj > 1:
            lift -= (1-aAdj)
        if (cPo.z <= (self.terrainXYHeight + self.mcMinHeight)):
            self.ctrans.z = self.mcMinHeight
        else:
            self.ctrans.z = lift
        self.camera.setHpr(self.camera, self.crot)
        self.camera.setPos(self.camera, self.ctrans)


    def ac_keys_handler(self, key):
        """
        Handle keys to simulate a aircraft
        """
        if key == 'i':
            self.ctrans.y += 0.01
        elif key == 'k':
            self.ctrans.y -= 0.01
        elif key == 'w':
            self.crot.y -= 0.01
        elif key == 's':
            self.crot.y += 0.01
        elif key == 'a':
            self.crot.x += 0.01
        elif key == 'd':
            self.crot.x -= 0.01
        elif key == 'q':
            self.crot.z -= 0.01
        elif key == 'e':
            self.crot.z += 0.01
        elif key == 'x':
            self.ctrans = Vec3(0,0,0)
            self.crot = Vec3(0,0,0)


    def setup_ac_keyshandler(self):
        self.mcMaxHeight = 10000
        self.mcMinHeight = 1
        self.mcMinAccel4PLift = 0.2
        self.mcMaxAngle4PLift = 60
        self.accept("w", self.ac_keys_handler, [ 'w' ])
        self.accept("s", self.ac_keys_handler, [ 's' ])
        self.accept("q", self.ac_keys_handler, [ 'q' ])
        self.accept("e", self.ac_keys_handler, [ 'e' ])
        self.accept("a", self.ac_keys_handler, [ 'a' ])
        self.accept("d", self.ac_keys_handler, [ 'd' ])
        self.accept("x", self.ac_keys_handler, [ 'x' ])
        self.accept("i", self.ac_keys_handler, [ 'i' ])
        self.accept("k", self.ac_keys_handler, [ 'k' ])
        for k in [ "w", "s", "q", "e", "a", "d", "x", "i", "k" ]:
            self.accept("{}-repeat".format(k), self.ac_keys_handler, [ k ])


    def prepare(self):
        if self.cfg['bP3DCameraControl']:
            self.useDrive()
        else:
            self.disableMouse()
        self.setup_lights()
        self.threadUpdate = threading.Thread(target=self.update_world_tf)
        self.update_world(self.cDefPos)
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
        'bDebug': False,
        'sTerrainFile': None,
        'bModeAC': False,
        'bTopView': False,
        'bLODBruteForce': False,
        'bP3DCameraControl': False,
        'LODAFMode': GeoMipTerrain.AFMOff,
        'iLODMinLevel': 0,
        }
    iArg = 0
    while iArg < (len(args)-1):
        iArg += 1
        cArg = args[iArg]
        if cArg.startswith("--s"):
            k = cArg[2:]
            iArg += 1
            cfg[k] = args[iArg]
        elif cArg.startswith("--i"):
            k = cArg[2:]
            iArg += 1
            cfg[k] = int(args[iArg], 0)
        elif cArg.startswith("--f"):
            k = cArg[2:]
            iArg += 1
            cfg[k] = float(args[iArg])
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
        elif cArg == "--help":
            print(cfg)
            exit()
    print("INFO:Args:",cfg)
    return cfg



print("FSim:", VERSION)
cfg = handle_args(sys.argv)
fsim = FSim(cfg)
fsim.prepare()
fsim.run()

