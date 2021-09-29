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

class Image:

    def __init__(self, fName, tag):
        self.fName = fName
        self.tag = tag
        self.rImg = skimage.io.imread(self.fName)
        self.gImg = gdal.Open(self.fName)
        self.XL, self.XD, t1, self.YT, t2, self.YD = self.gImg.GetGeoTransform()
        self.XW, self.YH = self.gImg.RasterXSize, self.gImg.RasterYSize


    def print_info(self):
        print("{}:".format(self.tag), self.XL, self.XD, self.XW, self.YT, self.YD, self.YH)



imgVeg = Image(fnVeg, "VEG")
imgVeg.print_info()

imgHF = Image(fnHF, "HF")
imgHF.print_info()


