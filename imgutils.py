#!/usr/bin/env python3
# Few helper logics to work with GeoTiff and Other images.
# This uses PIL for opening and saving and own logic for others.
# HanishKVC, 2021
# GPL


import PIL.Image
import numpy


gCfg = {}


class GTImage:

    def __init__(self, fName, tag, debug=False):
        self.fName = fName
        self.tag = tag
        self.debug = debug
        self.load()
        self.parse_geotiff()

    def print_info(self):
        print("{}:Lon".format(self.tag), self.sLon, self.dLon, self.eLon, self.XW)
        print("{}:Lat".format(self.tag), self.sLat, self.dLat, self.eLat, self.YH)
        print("{}:dim:{}:dtype:{}:min:{}:max:{}".format(self.tag, self.rImg.shape, self.rImg.dtype, self.rImg.min(), self.rImg.max()))

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
        self.pImg = PIL.Image.open(self.fName)
        try:
            if self.pImg.mode == 'P':
                tImg = numpy.array(self.pImg.convert('RGB'))
            else:
                tImg = numpy.array(self.pImg)
            self.rImg = GTImage.transpose(tImg)
        except RuntimeError:
            raise RuntimeError("{}: Image neither Gray or RGB".format(self.fName))

    @staticmethod
    def Save(fName, rImg2Save):
        trImg = GTImage.transpose(rImg2Save)
        print("SavingImgData:", trImg.shape, trImg.dtype, trImg.min(), trImg.max())
        tpImg =PIL.Image.fromarray(trImg)
        tpImg.save(fName)

    def save(self, fName=None, img2Save=None):
        if fName == None:
            fName = self.fName
        if type(img2Save) == type(None):
            img2Save = self.rImg
        GTImage.Save(fName, img2Save)

    def parse_geotiff(self):
        if PIL.TiffTags.TAGS[34737].upper() != 'GeoAsciiParamsTag'.upper():
            raise RuntimeError("ERRR:GTImage:GeoTiff TagMismatch wrt 34737")
        if PIL.TiffTags.TAGS[33922].upper() != 'ModelTiepointTag'.upper():
            raise RuntimeError("ERRR:GTImage:GeoTiff TagMismatch wrt 33922")
        if PIL.TiffTags.TAGS[33550].upper() != 'ModelPixelScaleTag'.upper():
            raise RuntimeError("ERRR:GTImage:GeoTiff TagMismatch wrt 33550")
        if PIL.TiffTags.TAGS[34264].upper() != 'ModelTransformationTag'.upper():
            raise RuntimeError("ERRR:GTImage:GeoTiff TagMismatch wrt 34264")
        try:
            if not self.pImg.tag[34737][0].upper().startswith('WGS'):
                raise RuntimeError("ERRR:GTImage:GeoTiff Not WGS based?")
        except:
            print("WARN:GTImage:GeoTiff GeoAsciiParamsTag missing")
        if self.pImg.tag.get(34264) == None:
            if (self.pImg.tag[33922][0] != 0) or (self.pImg.tag[33922][1] != 0) or (self.pImg.tag[33922][2] != 0):
                raise RuntimeError("ERRR:GTImage:GeoTiff ModelTiePoint not at 0,0,0 is unsupported")
            self.sLon = self.pImg.tag[33922][3]
            self.sLat = self.pImg.tag[33922][4]
            self.dLon = self.pImg.tag[33550][0]
            self.dLat = -1*self.pImg.tag[33550][1]
        else:
            if (self.pImg.tag[34264][1] != 0) or (self.pImg.tag[34264][2] != 0) or \
               (self.pImg.tag[34264][4] != 0) or (self.pImg.tag[34264][6] != 0) or \
               (self.pImg.tag[34264][8] != 0) or (self.pImg.tag[34264][9] != 0) or (self.pImg.tag[34264][10] != 0) or (self.pImg.tag[34264][11] != 0) or \
               (self.pImg.tag[34264][12] != 0) or (self.pImg.tag[34264][13] != 0) or (self.pImg.tag[34264][14] != 0) or (self.pImg.tag[34264][15] != 1) :
                raise RuntimeError("ERRR:GTImage:GeoTiff ModelTransformation other than 2d scaling and translation is unsupported")
            self.sLon = self.pImg.tag[34264][3]
            self.sLat = self.pImg.tag[34264][7]
            self.dLon = self.pImg.tag[34264][0]
            self.dLat = self.pImg.tag[34264][5]
        self.XW, self.YH = self.pImg.size
        self.eLon = self.sLon + self.XW*self.dLon
        self.eLat = self.sLat + self.YH*self.dLat
        # setup matrix transform for future/...
        # last 2 rows mimicing the identity matrix is important for translation to work,
        # as well as to have a invertible matrix (for being able to find a inverse of the matrix).
        self.xy2llTrans = numpy.array([[self.dLon,0,0,self.sLon],[0,self.dLat,0,self.sLat],[0,0,1,0],[0,0,0,1]])
        self.ll2xyTrans = numpy.linalg.inv(self.xy2llTrans)

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
    dtypeMax = numpy.iinfo(rImg.dtype).max
    noise = numpy.random.uniform(1-fNoiseRatio,1+fNoiseRatio,rImg.shape)
    #print(rImg[100,100], rImg[530,700])
    newC = rImg * noise
    newC[newC>dtypeMax] = dtypeMax
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
    #breakpoint()
    xS = yS = iBlurSize
    xE = rImg.shape[0]-iBlurSize
    yE = rImg.shape[1]-iBlurSize
    fImg = rImg/rImg.max()
    dImg = numpy.zeros(rImg.shape)
    # Handle the edge rows/cols
    #scaleBy = (iBlurSize*2+1)**2
    scaleBy = (iBlurSize+1)*2
    dImg[:iBlurSize] = fImg[:iBlurSize]*scaleBy
    dImg[-iBlurSize:] = fImg[-iBlurSize:]*scaleBy
    dImg[:,:iBlurSize] = fImg[:,:iBlurSize]*scaleBy
    dImg[:,-iBlurSize:] = fImg[:,-iBlurSize:]*scaleBy
    for x in range(-iBlurSize,iBlurSize):
        for y in range(-iBlurSize,iBlurSize):
            dImg[iBlurSize:-iBlurSize,:iBlurSize] += fImg[iBlurSize+x:-iBlurSize+x, iBlurSize+y:2*iBlurSize+y]
            dImg[iBlurSize:-iBlurSize,-iBlurSize:] += fImg[iBlurSize+x:-iBlurSize+x,-2*iBlurSize+y:-iBlurSize+y]
    for y in range(-iBlurSize,iBlurSize):
        for x in range(-iBlurSize,iBlurSize):
            dImg[:iBlurSize, iBlurSize:-iBlurSize] += fImg[iBlurSize+x:2*iBlurSize+x, iBlurSize+y:-iBlurSize+y]
            dImg[-iBlurSize:,iBlurSize:-iBlurSize] += fImg[-2*iBlurSize+x:-iBlurSize+x, iBlurSize+y:-iBlurSize+y]
    #dImg[iBlurSize:-iBlurSize,:iBlurSize] /= iBlurSize
    #dImg[iBlurSize:-iBlurSize,-iBlurSize:] /= iBlurSize
    cnt = 0
    for x in range(-iBlurSize,iBlurSize+1,1):
        for y in range(-iBlurSize,iBlurSize+1,1):
            cnt += 1
            dImg[xS:xE,yS:yE] += fImg[xS+x:xE+x, yS+y:yE+y]
    fImg = (dImg*rImg.max())/cnt
    rImg = numpy.round(fImg).astype(rImg.dtype)
    return rImg


def flip_img(rImg, bFlipVert=True):
    print("\tFlip")
    if bFlipVert:
        tImg = rImg[:,::-1]
    else:
        tImg = rImg[::-1,:]
    return tImg


def map_gray2color(imgS, imgR):
    """
    Color gray scale imgS to match equivalent map coord position color in imgR and return the same
    return rCM: the raw color map numpy array (i.e not a GTImage class instance)
    """
    rCM = numpy.zeros((imgS.rImg.shape[0], imgS.rImg.shape[1], imgR.rImg.shape[2]), dtype=imgR.rImg.dtype)
    print("MapGray2Color:", rCM.shape, rCM.dtype)
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
    if gCfg['bFlip']:
        rCM = flip_img(rCM,gCfg['bFlipVert'])
    return rCM


def handle_args(args, cb=None, bInitInternalCfg=True):
    """
    Put arguments which follow a standard template of
        --<[s|b|i|f]ArgKey> ArgValue
        into a dictionary.
    For other arguments it will call a callback passed to it.
        Else it will print the cfg dict till then and trigger exit.
        The callback if provided should return how many additional
        arguments (other than the arg pointed by iArg passed to it)
        it ate from the args list passed.
    """
    iArg = 0
    cfg = {
            'bMoreBluey': True,
            'bAddNoise': True,
            'fNoiseRatio': 0.1,
            'bBlur': True,
            'iBlurSize': 8,
            'bFlip': True,
            'bFlipVert': True,
            }
    while iArg < (len(args)-1):
        iArg += 1
        if args[iArg].startswith("--s"):
            theOpt = args[iArg][2:]
            cfg[theOpt] = args[iArg+1]
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
            if cb == None:
                print("FoundArgs:",cfg)
                exit()
            else:
                iArg += cb(args, iArg)
    if bInitInternalCfg:
        init(cfg)
    print(cfg)
    return cfg


def init(cfg):
    global gCfg
    gCfg = cfg


if __name__ == "__main__":
    print("ImgUtils: use this as a module")

