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

    def xy2coord(x,y):
        lon = self.sLon + self.dLon*x
        lat = self.sLat + self.dLat*y
        return lon, lat

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


def map_color(imgS, imgR):
    """
    Color gray scale imgS to match equivalent map coord position color in imgR and return the same
    """
    rCM = skimage.color.gray2rgb(imgS.rImg)
    for x in range(imgS.XW):
        for y in range(imgS.YH):
            lon, lat = imgS.xy2coord(x,y)
            color = imgR.get_coord(lon, lat)
            rCM[x,y] = color
    return rCM



imgVeg = Image(fnVeg, "VEG")
imgVeg.print_info()

imgHF = Image(fnHF, "HF")
imgHF.print_info()

rCM = map_color(imgHF, imgVeg)
skimage.io.imsave("{}.cm.png".format(imgHF.fName), rCM)

