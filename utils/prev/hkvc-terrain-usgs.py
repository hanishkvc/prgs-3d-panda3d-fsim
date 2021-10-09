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
import gdal


def handle_args(args):
    global fName, bBoost
    fName = args[1]
    bBoost = False
    iArg = 1
    while iArg < (len(args)-1):
        iArg += 1
        if args[iArg] == "--boost":
            bBoost = True


def geotiff_info(fName):
    g = gdal.Open(fName)
    fULX, fXD, t1, fULY, t2, fYD = g.GetGeoTransform()
    iXW = g.RasterXSize
    iYH = g.RasterYSize
    print("GeoTiff:ULX {}:XD {}:XW {}".format(fULX, fXD, iXW))
    print("GeoTiff:ULY {}:YD {}:YH {}".format(fULY, fYD, iYH))


handle_args(sys.argv)
# Load the image
print("INFO:LoadingImage:", fName)
fI = "{}".format(fName)
fOHF = "{}.hf.png".format(fName)
fOCM = "{}.cm.png".format(fName)
geotiff_info(fI)
iI = skimage.io.imread(fI)

# Adjust Image pixel values
def img_amplifylevels(iI, bBoostAmplify=True):
    if not bBoostAmplify:
        return iI/iI.max()
    iHist = numpy.histogram(iI,20)[0]
    iHTotal = numpy.sum(iHist)
    iMult = 1
    for i in range(4):
        iHPart = numpy.sum(iHist[:i+1])
        if (iHPart/iHTotal) > 0.9:
            iMult = int(6/(i+1))
            break
    iAmpd = (iI/iI.max())*iMult
    iC = numpy.clip(iAmpd, 0, 1)
    print("INFO:ImagePixelValueAdjust:", iMult)
    return iC


# Resize
def img_resize(iC):
    sNew = numpy.ceil(numpy.max(numpy.log2(iC.shape)))
    sNew = (2**sNew)+1 # Needed for Panda3D GeoMipTerrain
    iR = skimage.transform.resize(iC, (sNew,sNew))
    print("INFO:ImageResize:", sNew)
    return iR


iC = img_amplifylevels(iI, bBoost)
numpy.save("/tmp/10A.npy", iC)
iR = img_resize(iC)
numpy.save("/tmp/10R.npy", iR)
# Save the image
print("INFO:SavingImage:", fOHF)
skimage.io.imsave(fOHF, iR)


# Create ColorMap
# Maybe convert to NumPys parallel conditional indexing and updating, later
def img_hf2cm(iR):
    cN = skimage.color.gray2rgb(iR).astype(float)
    for x in range(iR.shape[0]):
        for y in range(iR.shape[1]):
            if iR[x,y] <= 0:
                cN[x,y] = [0, 0, 1]
            elif iR[x,y] < 0.20:
                gF = 0.2 + 0.8*(iR[x,y]/0.20)
                cN[x,y] = [0, gF, 0]
            elif iR[x,y] < 0.40:
                shade = 0.2 + 0.8*((iR[x,y]-0.20)/0.20)
                cN[x,y] = [0.5*shade, 0.25*shade, 0]
            else:
                cF = 0.2 + 0.8*((iR[x,y]-0.40)/0.60)
                cN[x,y] = cF
    return cN


# Flip image
def img_flip(cN, bVertFlip = True):
    if bVertFlip:
        cNF = cN[::-1,:]
    else:
        cNF = cN[:,::-1]
    return cNF


cN = img_hf2cm(iR)
cNF = img_flip(cN)
print("INFO:SavingImage:", fOCM)
skimage.io.imsave(fOCM, cNF)

