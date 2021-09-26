#!/bin/env python3
#
# hkvc-terrain-usgs.py - Make USGS elevation data suitable for my terrain heightfield
# HanishKVC, 2021
# GPL
#
# gmted2010 elevation data
#

import sys
import skimage.io
import skimage.transform
import numpy

# Load the image
fName = sys.argv[1]
print("INFO:LoadingImage:", fName)
fI = "{}".format(fName)
fO = "{}.hf.png".format(fName)
iI = skimage.io.imread(fI)

# Adjust Image pixel values
iHist = numpy.histogram(iI,20)[0]
iHTotal = numpy.sum(iHist)
iMult = 1
for i in range(4):
	iHPart = numpy.sum(iHist[:i+1])
	if (iHPart/iHTotal) > 0.9:
		iMult = int(20/(i+1))
		break
iAmpd = (iI/iI.max())*iMult
iC = numpy.clip(iAmpd, 0, 1)
print("INFO:ImagePixelValueAdjust:", iMult)

# Resize
sMax = numpy.max(numpy.log2(iC.shape))
if float(int(sMax)) == sMax:
	sNew = int(sMax)
else:
	sNew = int(sMax)+1
sNew = (2**sNew)+1 # Needed for Panda3D GeoMipTerrain
iR = skimage.transform.resize(iC, (sNew,sNew))
print("INFO:ImageResize:", sNew)

# Save the image
print("INFO:SavingImage:", fO)
skimage.io.imsave(fO, iR)

