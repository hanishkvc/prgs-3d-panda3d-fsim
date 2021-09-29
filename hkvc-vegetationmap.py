#!/usr/bin/env python3
# Created World Vegetation NDVI data based colormap for heightfields
# HanishKVC, 2021
# GPL

import sys
import skimage.io
import numpy
import gdal

fnVeg = sys.argv[1]
fnHF = sys.argv[2]

imgVeg = skimage.io.imread(fnVeg)
imgHF = skimage.io.imread(fnHF)

gVeg = gdal.Open(fnVeg)
gHF = gdal.Open(fnHF)

vegXL, vegXD, t1, vegYT, t2, vegYD = gVeg.GetGeoTransform()
hfXL, hfXD, t1, hfYT, t2, hfYD = gHF.GetGeoTransform()

print(vegXL, vegXD, vegYT, vegYD)
print(hfXL, hfXD, hfYT, hfYD)


