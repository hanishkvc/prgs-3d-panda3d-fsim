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
        self.sLon, self.dLon, t1, self.sLat, t2, self.dLat = self.gImg.GetGeoTransform()
        self.XW, self.YH = self.gImg.RasterXSize, self.gImg.RasterYSize
        self.eLon = self.sLon + self.XW*self.dLon
        self.eLat = self.sLat + self.YH*self.dLat

    def print_info(self):
        print("{}:Lon".format(self.tag), self.sLon, self.dLon, self.eLon, self.XW)
        print("{}:Lat".format(self.tag), self.sLat, self.dLat, self.eLat, self.YH)

    def get_xy(x,y):
        return self.rImg[x,y]

    def coord2xy(lon, lat):
        if (lon < self.sLon) or (lon > self.eLon):
            return None
        if (lat > self.sLat) or (lat < self.eLat):
            return None
        cLonDelta = lon - self.sLon
        x = cLonDelta/self.dLon
        cLatDelta = lat - self.sLat
        y = cLatDelta/self.dLat
        return x,y

    def get_coord(lon, lat):
        x,y = self.coord2xy(lon, lat)
        return self.get_xy(x,y)



imgVeg = Image(fnVeg, "VEG")
imgVeg.print_info()

imgHF = Image(fnHF, "HF")
imgHF.print_info()


