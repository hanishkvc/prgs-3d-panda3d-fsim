#!/bin/env python3
#
# hkvc-terrain-usgs.py - Make USGS elevation data suitable for my terrain heightfield and a corresponding crude auto colormap
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
fOHF = "{}.hf.png".format(fName)
fOCM = "{}.cm.png".format(fName)
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
print("INFO:SavingImage:", fOHF)
skimage.io.imsave(fOHF, iR)


# Create ColorMap
# Maybe convert to NumPys parallel conditional indexing and updating, later
cN = skimage.color.gray2rgb(iR).astype(float)
for x in range(iR.shape[0]):
    for y in range(iR.shape[1]):
        if iR[x,y] == 0:
            cN[x,y] = [0, 0, 1]
        elif iR[x,y] < 0.25:
            gF = 0.2 + 0.8*(iR[x,y]/0.25)
            cN[x,y] = [0, gF, 0]
        elif iR[x,y] < 0.50:
            rF = 0.2 + 0.8*((iR[x,y]-0.25)/0.25)
            cN[x,y] = [rF, 0, 0]
        else:
            cF = 0.2 + 0.8*((iR[x,y]-0.50)/0.50)
            cN[x,y] = cF

# Flip image
bVertFlip = True
if bVertFlip:
    cNF = cN[::-1,:]
else:
    cNF = cN[:,::-1]

print("INFO:SavingImage:", fOCM)
skimage.io.imsave(fOCM, cNF)

