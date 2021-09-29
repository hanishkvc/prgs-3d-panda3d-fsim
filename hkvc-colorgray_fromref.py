#!/usr/bin/env python3
# Color a Grayscale image based on color at corresponding location in a reference image
# The grayscale and reference images need to be GeoTiff images.
# The Color image generated will be a png.
# This can be used to color say a heightfield image based on World Vegetation NDVI data
# HanishKVC, 2021
# GPL

import sys
import skimage.io
import numpy
import gdal


class Image:

    def __init__(self, fName, tag):
        self.fName = fName
        self.tag = tag
        tImg = skimage.io.imread(self.fName)
        if len(tImg.shape) == 2:
            self.rImg = tImg.transpose()
        elif len(tImg.shape) == 3:
            self.rImg = tImg.transpose(1,0,2)
        else:
            raise RuntimeError("{}: Image neither Gray or RGB".format(self.fName))
        self.gImg = gdal.Open(self.fName)
        self.sLon, self.dLon, t1, self.sLat, t2, self.dLat = self.gImg.GetGeoTransform()
        self.XW, self.YH = self.gImg.RasterXSize, self.gImg.RasterYSize
        self.eLon = self.sLon + self.XW*self.dLon
        self.eLat = self.sLat + self.YH*self.dLat

    def print_info(self):
        print("{}:Lon".format(self.tag), self.sLon, self.dLon, self.eLon, self.XW)
        print("{}:Lat".format(self.tag), self.sLat, self.dLat, self.eLat, self.YH)

    def getpixel_xy(self, x,y):
        return self.rImg[x,y]

    def xy2coord(self, x,y):
        lon = self.sLon + self.dLon*x
        lat = self.sLat + self.dLat*y
        return lon, lat

    def coord2xy(self, lon, lat):
        if (lon < self.sLon) or (lon > self.eLon):
            return None
        if (lat > self.sLat) or (lat < self.eLat):
            return None
        cLonDelta = lon - self.sLon
        x = cLonDelta/self.dLon
        cLatDelta = lat - self.sLat
        y = cLatDelta/self.dLat
        return round(x),round(y)

    def getpixel_coord(self, lon, lat):
        x,y = self.coord2xy(lon, lat)
        return self.getpixel_xy(x,y)


def map_color(imgS, imgR):
    """
    Color gray scale imgS to match equivalent map coord position color in imgR and return the same
    """
    rCM = skimage.color.gray2rgb(imgS.rImg)
    for x in range(imgS.XW):
        for y in range(imgS.YH):
            lon, lat = imgS.xy2coord(x,y)
            color = imgR.getpixel_coord(lon, lat)
            rCM[x,y] = color
    return rCM


def handle_args(args):
    iArg = 0
    while iArg < (len(args)-1):
        iArg += 1
        if args[iArg] == "--ref":
            refFName = args[iArg+1]
            iArg += 1
        elif args[iArg] == "--src":
            srcFName = args[iArg+1]
            iArg += 1
    return refFName, srcFName


def run_main():
    fnRef, fnSrc = handle_args(sys.argv)
    imgRef = Image(fnRef, "REF")
    imgRef.print_info()
    imgSrc = Image(fnSrc, "Src")
    imgSrc.print_info()

    rCM = map_color(imgSrc, imgRef)
    skimage.io.imsave("{}.cm.png".format(imgSrc.fName), rCM)


if __name__ == "__main__":
    run_main()

