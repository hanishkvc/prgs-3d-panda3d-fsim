#!/usr/bin/env python3

from direct.showbase.ShowBase import ShowBase

gSB = ShowBase()
gGnd = gSB.loader.loadModel("models/environment")
gGnd.reparentTo(gSB.render)

gSB.run()

