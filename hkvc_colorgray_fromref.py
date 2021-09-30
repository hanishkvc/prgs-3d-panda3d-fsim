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


class GTImage:

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
            raise RuntimeError("GTImage: Image neither Gray or RGB")
        return rImg

    def load(self, fName=None):
        if fName == None:
            fName = self.fName
        else:
            self.fName = fName
        tImg = skimage.io.imread(self.fName)
        try:
            self.rImg = GTImage.transpose(tImg)
        except RuntimeError:
            raise RuntimeError("{}: Image neither Gray or RGB".format(self.fName))

    @staticmethod
    def Save(fName, img2Save):
        tImg = GTImage.transpose(img2Save)
        skimage.io.imsave(fName, tImg)

    def save(self, fName=None, img2Save=None):
        if fName == None:
            fName = self.fName
        if type(img2Save) == type(None):
            img2Save = self.rImg
        GTImage.Save(fName, img2Save)

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


def add_noise(rImg, fNoiseRatio=0.1):
    """
    Add noise to all channels of passed raw image (numpy array).
    The max of random amount of noise added is controlled by fNoiseRatio.

    As saturation arithmatic not directly supported by numpy / python
    So for now apply a simple randomly generated multiplier.
    Note that with this the noise applied also varies proportional to current value
    in each pixel/location. And inturn for locations with 0 value, nothing is applied.
    """
    print("\tAddNoise")
    noise = numpy.random.uniform(1-fNoiseRatio,1+fNoiseRatio,rImg.shape)
    #print(rImg[100,100], rImg[530,700])
    newC = rImg * noise
    rImg = numpy.round(newC).astype(rImg.dtype)
    #print(rImg[100,100], rImg[530,700])
    return rImg


def blur_filter(rImg, iBlurSize=1):
    """
    Blur all channels of passed raw image (numpy array) by doing a NxN based filtering
    where each pixel is averaged from a window around its position
    of size -iBlurSize to +iBlurSize along x and y axis.
    """
    print("\tBlur")
    xS = yS = iBlurSize
    xE = rImg.shape[0]-iBlurSize
    yE = rImg.shape[1]-iBlurSize
    fImg = rImg/rImg.max()
    dImg = numpy.zeros(rImg.shape)
    cnt = 0
    for x in range(-iBlurSize,iBlurSize+1,1):
        for y in range(-iBlurSize,iBlurSize+1,1):
            cnt += 1
            dImg[xS:xE,yS:yE] += fImg[xS+x:xE+x, yS+y:yE+y]
    fImg = (dImg*rImg.max())/cnt
    rImg = numpy.round(fImg).astype(rImg.dtype)
    return rImg


def map_color(imgS, imgR):
    """
    Color gray scale imgS to match equivalent map coord position color in imgR and return the same
    return rCM: the raw color map numpy array (i.e not a GTImage class instance)
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
        rCM = add_noise(rCM,gCfg['fNoiseRatio'])
    if gCfg['bBlur']:
        rCM = blur_filter(rCM,gCfg['iBlurSize'])
    return rCM


def handle_args(args):
    iArg = 0
    cfg = {
            'refFName': None,
            'srcFName': None,
            'bMoreBluey': True,
            'bAddNoise': True,
            'fNoiseRatio': 0.1,
            'bBlur': True,
            'iBlurSize': 8,
            }
    while iArg < (len(args)-1):
        iArg += 1
        if args[iArg] == "--ref":
            cfg['refFName'] = args[iArg+1]
            iArg += 1
        elif args[iArg] == "--src":
            cfg['srcFName'] = args[iArg+1]
            iArg += 1
        elif args[iArg].startswith("--b"):
            theOpt = args[iArg][2:]
            if args[iArg+1].upper() in [ "FALSE", "NO", "VENDA", "BEDA", "NAHI" ]:
                cfg[theOpt] = False
            else:
                cfg[theOpt] = True
            iArg += 1
        elif args[iArg].startswith("--i"):
            theOpt = args[iArg][2:]
            cfg[theOpt] = int(args[iArg+1])
            iArg += 1
        elif args[iArg].startswith("--f"):
            theOpt = args[iArg][2:]
            cfg[theOpt] = float(args[iArg+1])
            iArg += 1
        else:
            print("Args:",cfg)
            exit()
    print(cfg)
    return cfg


def run_main():
    imgRef = GTImage(gCfg['refFName'], "REF")
    imgRef.print_info()
    imgSrc = GTImage(gCfg['srcFName'], "Src")
    imgSrc.print_info()

    rCM = map_color(imgSrc, imgRef)
    fnCM = "{}.cm.png".format(imgSrc.fName)
    GTImage.Save(fnCM, rCM)


if __name__ == "__main__":
    gCfg = handle_args(sys.argv)
    run_main()

