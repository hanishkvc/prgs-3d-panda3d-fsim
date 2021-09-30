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

    def __init__(self, fName, tag, debug=False):
        self.fName = fName
        self.tag = tag
        self.debug = debug
        self.load()
        self.gImg = gdal.Open(self.fName)
        self.sLon, self.dLon, t1, self.sLat, t2, self.dLat = self.gImg.GetGeoTransform()
        self.XW, self.YH = self.gImg.RasterXSize, self.gImg.RasterYSize
        self.eLon = self.sLon + self.XW*self.dLon
        self.eLat = self.sLat + self.YH*self.dLat

    def print_info(self):
        print("{}:Lon".format(self.tag), self.sLon, self.dLon, self.eLon, self.XW)
        print("{}:Lat".format(self.tag), self.sLat, self.dLat, self.eLat, self.YH)

    @staticmethod
    def transpose(tImg):
        if len(tImg.shape) == 2:
            rImg = tImg.transpose()
        elif len(tImg.shape) == 3:
            rImg = tImg.transpose(1,0,2)
        else:
            raise RuntimeError("Image: Image neither Gray or RGB")
        return rImg

    def load(self, fName=None):
        if fName == None:
            fName = self.fName
        else:
            self.fName = fName
        tImg = skimage.io.imread(self.fName)
        try:
            self.rImg = Image.transpose(tImg)
        except RuntimeError:
            raise RuntimeError("{}: Image neither Gray or RGB".format(self.fName))

    @staticmethod
    def Save(fName, img2Save):
        tImg = Image.transpose(img2Save)
        skimage.io.imsave(fName, tImg)

    def save(self, fName=None, img2Save=None):
        if fName == None:
            fName = self.fName
        if type(img2Save) == type(None):
            img2Save = self.rImg
        Image.Save(fName, img2Save)

    def getpixel_xy(self, x,y):
        return self.rImg[x,y]

    def xy2coord(self, x,y):
        lon = self.sLon + self.dLon*x
        lat = self.sLat + self.dLat*y
        if self.debug:
            print("DBUG:XY2MCO:{}:{:011.5f}, {:011.5f}:{:011.5f}, {:011.5f}".format(self.tag,x,y,lon,lat))
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
        if self.debug:
            print("DBUG:MCO2XY:{}:{:011.5f}, {:011.5f}:{:011.5f}, {:011.5f}".format(self.tag,lon,lat,x,y))
        return round(x),round(y)

    def getpixel_coord(self, lon, lat):
        x,y = self.coord2xy(lon, lat)
        return self.getpixel_xy(x,y)


def add_noise(rImg, percent=0.1):
    """
    Add noise to all channels of passed raw image (numpy array)
    """
    # As saturation arithmatic not directly supported by numpy / python
    # So for now apply a simple randomly generated multiplier
    # Note that with this the noise applied also varies proportional to current value
    # in each pixel/location. And inturn for locations with 0, nothing is applied.
    print("\tAddNoise")
    noise = numpy.random.uniform(1-percent,1+percent,rImg.shape)
    #print(rImg[100,100], rImg[530,700])
    newC = rImg * noise
    rImg = numpy.round(newC).astype(rImg.dtype)
    #print(rImg[100,100], rImg[530,700])
    return rImg


def blur_filter(rImg, width=1):
    """
    Blur all channels of passed raw image (numpy array)
    """
    # do a 3x3 based filter
    print("\tLowPass")
    fImg = rImg/rImg.max()
    fImg[1:-1,1:-1] = \
        ( \
        fImg[0:-2,0:-2] + fImg[1:-1,0:-2] + fImg[2:,0:-2] + \
        fImg[0:-2,1:-1] + fImg[1:-1,1:-1] + fImg[2:,1:-1] + \
        fImg[0:-2,2:  ] + fImg[1:-1,2:  ] + fImg[2:,2:  ] \
        ) / 9
    fImg = fImg*rImg.max()
    rImg = numpy.round(fImg).astype(rImg.dtype)
    return rImg


def map_color(imgS, imgR):
    """
    Color gray scale imgS to match equivalent map coord position color in imgR and return the same
    return rCM: the raw color map numpy array (i.e not a Image class instance)
    """
    rCM = numpy.zeros((imgS.rImg.shape[0],imgS.rImg.shape[1],imgR.rImg.shape[2]), dtype=numpy.uint16)
    print("MapColor", rCM.shape, rCM.dtype)
    if gCfg['bMoreBluey']:
        cmThreshold = int(numpy.iinfo(rCM.dtype).max/2)
        print("BlueThreshold", cmThreshold)
    for x in range(imgS.XW):
        for y in range(imgS.YH):
            lon, lat = imgS.xy2coord(x,y)
            color = imgR.getpixel_coord(lon, lat)
            if gCfg['bMoreBluey'] and (color[0] == 0) and (color[1] == 0):
                if color[2] < cmThreshold:
                    color[2] = 0.5*cmThreshold + color[2]*1.2
            rCM[x,y] = color
    if gCfg['bAddNoise']:
        rCM = add_noise(rCM)
    if gCfg['bLowPass']:
        rCM = blur_filter(rCM)
    return rCM


def handle_args(args):
    iArg = 0
    cfg = {
            'bMoreBluey': True,
            'refFName': None,
            'srcFName': None,
            'bAddNoise': True,
            'bLowPass': True,
            }
    while iArg < (len(args)-1):
        iArg += 1
        if args[iArg] == "--ref":
            cfg['refFName'] = args[iArg+1]
            iArg += 1
        elif args[iArg] == "--src":
            cfg['srcFName'] = args[iArg+1]
            iArg += 1
        elif args[iArg] in [ "--bMoreBluey", "--bAddNoise", "--bLowPass" ]:
            theOpt = args[iArg][2:]
            if args[iArg+1].upper() in [ "FALSE", "NO" ]:
                cfg[theOpt] = False
            else:
                cfg[theOpt] = True
            iArg += 1
    print(cfg)
    return cfg


def run_main():
    imgRef = Image(gCfg['refFName'], "REF")
    imgRef.print_info()
    imgSrc = Image(gCfg['srcFName'], "Src")
    imgSrc.print_info()

    rCM = map_color(imgSrc, imgRef)
    fnCM = "{}.cm.png".format(imgSrc.fName)
    Image.Save(fnCM, rCM)


if __name__ == "__main__":
    gCfg = handle_args(sys.argv)
    run_main()

