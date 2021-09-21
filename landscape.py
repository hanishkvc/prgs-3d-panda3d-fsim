#!/usr/bin/env python3

from direct.showbase.ShowBase import ShowBase
from direct.task import Task


def move_camera(task):
    g['CamX'] += 0.1
    g['SB'].camera.setPos(g['CamX'], g['CamY'], g['CamZ'])
    g['SB'].camera.setHpr(0, 0, 0)
    return Task.cont


def init(g):
    g['SB'] = ShowBase()
    g['Gnd'] = g['SB'].loader.loadModel("models/environment")
    g['Gnd'].reparentTo(g['SB'].render)
    g['CamX'] = 0
    g['CamY'] = 0
    g['CamZ'] = 1


def prepare(g):
    g['SB'].taskMgr.add(move_camera, 'MoveCameraTsk')


g = {}
init(g)
prepare(g)
g['SB'].run()

