#!/usr/bin/env python3

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import GeoMipTerrain


def set_camera(g):
    g['SB'].camera.setPos(g['CamX'], g['CamY'], g['CamZ'])
    g['SB'].camera.setHpr(0, 0, 0)


def move_camera(task):
    if (task.frame%24) == 0:
        g['CamX'] += 0.1
    set_camera(g)
    return Task.cont


def init(g):
    g['SB'] = ShowBase()
    if False:
        g['Gnd'] = g['SB'].loader.loadModel("models/environment")
        g['Gnd'].reparentTo(g['SB'].render)
    else:
        g['Gnd'] = GeoMipTerrain("Gnd")
        g['Gnd'].setHeightfield("./gnd_hm.jpg")
        g['Gnd'].setBlockSize(32)
        g['Gnd'].setNear(40)
        g['Gnd'].setFar(100)
        g['Gnd'].setFocalPoint(g['SB'].camera)
        g['Gnd'].getRoot().reparentTo(g['SB'].render)
        g['Gnd'].getRoot().setSz(100)
        g['Gnd'].generate()
    g['CamX'] = 0
    g['CamY'] = 0
    g['CamZ'] = 250
    set_camera(g)


def prepare(g):
    g['SB'].useDrive()
    #g['SB'].taskMgr.add(move_camera, 'MoveCameraTsk')


g = {}
init(g)
prepare(g)
g['SB'].run()

