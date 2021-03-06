#!/usr/bin/env python3
# Few helper logics to work with GeoTiff and Other images.
# This uses PIL for opening and saving and own logic for others.
# HanishKVC, 2021
# GPL


import PIL.Image
import numpy
import PIL.PngImagePlugin

import odb


gCfg = {
        'bDebug': False,
        'bBoostAmplify': False,
        'bMoreBluey': True,
        'bAddNoise': True,
        'fNoiseRatio': 0.1,
        'bBlur': True,
        'iBlurSize': 8,
        'bBlurEdges': True,
        'bFlip': True,
        'bFlipVert': True,
        'iResizeFilter': PIL.Image.BILINEAR,
        }


class GTImage:

    def __init__(self, fName, tag, debug=None):
        self.fName = fName
        self.tag = tag
        if debug == None:
            debug = gCfg['bDebug']
        self.debug = debug
        self.load()
        self.parse_geotiff()

    def print_info(self):
        print("{}:Lon".format(self.tag), self.sLon, self.dLon, self.eLon, self.XW)
        print("{}:Lat".format(self.tag), self.sLat, self.dLat, self.eLat, self.YH)
        print("{}:dim:{}:dtype:{}:min:{}:max:{}".format(self.tag, self.rImg.shape, self.rImg.dtype, self.rImg.min(), self.rImg.max()))

    def get_pnginfo(self):
        info = PIL.PngImagePlugin.PngInfo()
        info.add_text("SLon", str(self.sLon))
        info.add_text("ELon", str(self.eLon))
        info.add_text("SLat", str(self.sLat))
        info.add_text("ELat", str(self.eLat))
        return info

    def load(self, fName=None, bTranspose=True):
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
            if bTranspose:
                self.rImg = transpose_rimg(tImg)
        except RuntimeError:
            raise RuntimeError("{}: Image neither Gray or RGB".format(self.fName))

    def save(self, fName=None, rImg2Save=None, bTranspose=True):
        if fName == None:
            fName = self.fName
        if type(rImg2Save) == type(None):
            rImg2Save = self.rImg
        save_rimg(fName, rImg2Save, bTranspose)

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


def load_rimg(fName, bTranspose=False):
    pImg = PIL.Image.open(fName)
    rImg = numpy.array(pImg)
    if bTranspose:
        trImg = transpose_rimg(rImg)
    else:
        trImg = rImg
    return trImg


def to_uint8(dIn, minV=None, maxV=None, bExpand=False):
    """
    Convert given dIn data array into an array of uint8 type.
    If minV, maxV are given then map this into the full uint8 space.
    Else if Expand is given then map the min and or max in passed data into full uint8 space.
    Else if not Expand then map the min and or max of dIn.dtype into full uint8 space.
    """
    #breakpoint()
    if maxV == None:
        if bExpand:
            maxV = float(dIn.max())
        else:
            maxV = float(numpy.iinfo(dIn.dtype).max)
    if minV == None:
        if bExpand:
            minV = float(dIn.min())
        else:
            minV = float(numpy.iinfo(dIn.dtype).min)
    if gCfg['bDebug']:
        print("INFO:2Uint8:", dIn.min(), dIn.max(), "expected range:", minV, maxV)
    if (dIn.min() < minV) or (dIn.max() > maxV):
        raise RuntimeError("2UInt8: Data beyond expected range of {} to {}".format(minV, maxV))
    dTmp = (dIn-minV)/(maxV-minV)
    dOut = dTmp*255
    dOut = dOut.astype(numpy.uint8)
    return dOut


def save_rimg(fName, rImg, bTranspose=False, bExpand=False, pngInfo=None):
    """
    Save the raw image data array into a image file containing 8bit entities.
        ie for gray its 8bit gray shades and for color its 8bit R, 8bit G and 8bit B values.
    If the raw image data is
        float, then its expected to be in the range 0.0 to 1.0.
        int32, then its expected to be either in the range 0 to MaxInt or -MinInt to MaxInt.
    If saving into a png file, one can pass additional info to store in the image using
        the pngInfo argument.
    """
    if bTranspose:
        trImg = transpose_rimg(rImg)
    else:
        trImg = rImg
    print("imgutils:SavingRImg:", trImg.shape, trImg.dtype, trImg.min(), trImg.max())
    if trImg.dtype == numpy.int32:
        trImg = to_uint8(trImg, bExpand=bExpand)
        print("imgutils:SavingRImg:Adjust:", trImg.shape, trImg.dtype, trImg.min(), trImg.max())
    elif (trImg.dtype == numpy.float64) or (trImg.dtype == numpy.float32):
        if bExpand:
            trImg = to_uint8(trImg, bExpand=bExpand)
        else:
            trImg = to_uint8(trImg, 0.0, 1.0)
        print("imgutils:SavingRImg:Adjust:", trImg.shape, trImg.dtype, trImg.min(), trImg.max())
    tpImg =PIL.Image.fromarray(trImg)
    if pngInfo == None:
        tpImg.save(fName)
    else:
        tpImg.save(fName, pnginfo=pngInfo)


def transpose_rimg(rImg):
    print("\tTranspose")
    if len(rImg.shape) == 2:
        rImg = rImg.transpose()
    elif len(rImg.shape) == 3:
        rImg = rImg.transpose(1,0,2)
    else:
        raise RuntimeError("imgutils:TransposeRImg: Image neither Gray or RGB")
    return rImg


def resize_pwrof2square_rimg(rImg, extra=0, resizeFilter=-1):
    """
    Resize a given raw image to be a square which has powerof2 dimensions.
    The resultant image could be larger than either of the input dimensions, if they werent powersof2.
    It also allows a additional extra size to be added beyond powerof2.
        This (rather extra=1) is needed by Panda3D GeoMipTerrain files.
    NOTE: Currently it uses PIL Image resize.
    """
    sNew = numpy.ceil(numpy.max(numpy.log2(rImg.shape)))
    sNew = int((2**sNew)+extra)
    return resize_rimg(rImg, sNew, sNew, resizeFilter)


def resize_rimg(rImg, xs, ys, resizeFilter=-1):
    """
    Resize the given raw image to specified size.
    resizeFilter specifies the filter to use. Refer to PIL.Image documentation for the options.
    """
    pImg =PIL.Image.fromarray(rImg)
    if resizeFilter < 0:
        resizeFilter = PIL.Image.BILINEAR
    print("\tImageResize", rImg.shape, xs, ys, resizeFilter)
    prImg=pImg.resize((xs, ys), resample=resizeFilter)
    return numpy.array(prImg)


def crop_rimg(rImg, xStartOrSize, yStartOrSize, xEnd=None, yEnd=None):
    """
    Crop the passed image data.
    One could either specify the start and end positions wrt x and y OR
    One could specify the size of image needed along x and y axis.
    """
    if xEnd == None:
        xStart = 0
        yStart = 0
        xEnd = xStartOrSize
        yEnd = yStartOrSize
    else:
        xStart = xStartOrSize
        yStart = yStartOrSize
    print("\tCrop", xStart, yStart, xEnd, yEnd)
    rNew = rImg[xStart:xEnd,yStart:yEnd]
    return rNew


def add_noise_rimg(rImg, fNoiseRatio=0.1):
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


def blur_filter_rimg(rImg, iBlurSize=1, bBlurEdges=True):
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
    if bBlurEdges:
        scaleBy = (iBlurSize+1)*2
        dImg[:iBlurSize] = fImg[:iBlurSize]*scaleBy
        dImg[-iBlurSize:] = fImg[-iBlurSize:]*scaleBy
        dImg[:,:iBlurSize] = fImg[:,:iBlurSize]*scaleBy
        dImg[:,-iBlurSize:] = fImg[:,-iBlurSize:]*scaleBy
        for x in range(-iBlurSize,iBlurSize):
            for y in range(-iBlurSize,iBlurSize):
                # top and bottom bands
                dImg[iBlurSize:-iBlurSize,:iBlurSize] += fImg[iBlurSize+x:-iBlurSize+x, iBlurSize+y:2*iBlurSize+y]
                dImg[iBlurSize:-iBlurSize,-iBlurSize:] += fImg[iBlurSize+x:-iBlurSize+x,-2*iBlurSize+y:-iBlurSize+y]
                # left and right bands
                dImg[:iBlurSize, iBlurSize:-iBlurSize] += fImg[iBlurSize+x:2*iBlurSize+x, iBlurSize+y:-iBlurSize+y]
                dImg[-iBlurSize:,iBlurSize:-iBlurSize] += fImg[-2*iBlurSize+x:-iBlurSize+x, iBlurSize+y:-iBlurSize+y]
                # corners
                dImg[:iBlurSize,:iBlurSize] += fImg[iBlurSize+x:2*iBlurSize+x,iBlurSize+y:2*iBlurSize+y]
                dImg[-iBlurSize:,-iBlurSize:] += fImg[-2*iBlurSize+x:-iBlurSize+x,-2*iBlurSize+y:-iBlurSize+y]
                dImg[-iBlurSize:,:iBlurSize] += fImg[-2*iBlurSize+x:-iBlurSize+x,iBlurSize+y:2*iBlurSize+y]
                dImg[:iBlurSize,-iBlurSize:] += fImg[iBlurSize+x:2*iBlurSize+x,-2*iBlurSize+y:-iBlurSize+y]
    else:
        scaleBy = (2*iBlurSize+1)**2
        dImg[:iBlurSize] = fImg[:iBlurSize]*scaleBy
        dImg[-iBlurSize:] = fImg[-iBlurSize:]*scaleBy
        dImg[:,:iBlurSize] = fImg[:,:iBlurSize]*scaleBy
        dImg[:,-iBlurSize:] = fImg[:,-iBlurSize:]*scaleBy
    # Handle the non edge parts
    cnt = 0
    for x in range(-iBlurSize,iBlurSize+1,1):
        for y in range(-iBlurSize,iBlurSize+1,1):
            cnt += 1
            dImg[xS:xE,yS:yE] += fImg[xS+x:xE+x, yS+y:yE+y]
    # scale/average it
    fImg = (dImg*rImg.max())/cnt
    rImg = numpy.round(fImg).astype(rImg.dtype)
    return rImg


def flip_rimg(rImg, bFlipVert=True):
    print("\tFlip")
    if bFlipVert:
        tImg = rImg[:,::-1]
    else:
        tImg = rImg[::-1,:]
    return tImg


def hf2cm_rimg(rImg):
    """
    Create ColorMap for the given heightfield image, based on the height (color/shade value).
    ToThink: Maybe convert to NumPys parallel conditional indexing and updating, later.
    """
    print("\tHF2CM")
    if (rImg.dtype != numpy.float64) and (rImg.dtype != numpy.float32):
        maxV = numpy.iinfo(rImg.dtype).max
        rImg = rImg/maxV
    cN = numpy.zeros((rImg.shape[0], rImg.shape[1], 3), dtype=numpy.float64)
    for x in range(rImg.shape[0]):
        for y in range(rImg.shape[1]):
            if rImg[x,y] <= 0:
                cN[x,y] = [0, 0, 1]
            elif rImg[x,y] < 0.20:
                gF = 0.2 + 0.8*(rImg[x,y]/0.20)
                cN[x,y] = [0, gF, 0]
            elif rImg[x,y] < 0.40:
                shade = 0.2 + 0.8*((rImg[x,y]-0.20)/0.20)
                cN[x,y] = [0.5*shade, 0.25*shade, 0]
            else:
                cF = 0.2 + 0.8*((rImg[x,y]-0.40)/0.60)
                cN[x,y] = cF
    return cN


def map_objects_gti(imgS, db):
    """
    For the given GeoTiff image, check if any objects are there in the given objects db, in the corresponding region.
    """
    ll = []
    for x in range(imgS.XW):
        for y in range(imgS.YH):
            lon, lat = imgS.xy2coord(x,y)
            obj = odb.get(db, lat, lon)
            if obj != None:
                ll.append([x, y, obj['icao']])
    return ll


def mapto_ex_gti(imgS, imgR):
    """
    MapToExtended: Create new raw image which maps the given imgS to match equivalent map coord position colors in imgR.
    imgS and imgR should be of GTImage type.
    return rCM: the raw color map numpy array (i.e not a GTImage class instance)
    It optionally applies some noise, blur and flip operations, if requested.
    """
    rCM = numpy.zeros((imgS.rImg.shape[0], imgS.rImg.shape[1], imgR.rImg.shape[2]), dtype=imgR.rImg.dtype)
    print("\tMapToExtended:", rCM.shape, rCM.dtype)
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
        rCM = add_noise_rimg(rCM,gCfg['fNoiseRatio'])
    if gCfg['bBlur']:
        rCM = blur_filter_rimg(rCM,gCfg['iBlurSize'],gCfg['bBlurEdges'])
    if gCfg['bFlip']:
        rCM = flip_rimg(rCM,gCfg['bFlipVert'])
    return rCM


def reduce_shades_crude_rimg(rImg, numShades=8, blurSize=4):
    """
    Reduce the color/shades in the image to contain only numShades number of them.
    Inturn apply a blur filter to smooth it a bit.
    """
    print("\tReduceShadesCrude")
    if rImg.dtype == numpy.int32:
        baseDiv = 256
    else:
        baseDiv = 1
    div = baseDiv*numShades
    print(rImg.shape, rImg.dtype, baseDiv, numShades, div)
    tImg = numpy.round(rImg/div)*numShades
    tImg[tImg > 255] = 255
    numpy.unique(tImg)
    tImg=tImg.astype(numpy.uint8)
    tImg=blur_filter_rimg(tImg, blurSize)
    numpy.unique(tImg)
    return tImg


def amplify_shades_fimg(fImg, bBoostAmplify=True):
    """
    Increase Image pixel values.
    This returns a image data array with floats in range 0 to 1.
    """
    if not bBoostAmplify:
        return fImg/fImg.max()
    iHist = numpy.histogram(fImg,20)[0]
    iHTotal = numpy.sum(iHist)
    iMult = 1
    for i in range(4):
        iHPart = numpy.sum(iHist[:i+1])
        if (iHPart/iHTotal) > 0.9:
            iMult = int(6/(i+1))
            break
    print("\tAmplifyShades", iMult)
    ampdImg = (fImg/fImg.max())*iMult
    clippedImg = numpy.clip(ampdImg, 0, 1)
    return clippedImg


def amplify_shades_rimg(rImg, bBoostAmplify=True):
    maxV = numpy.iinfo(rImg.dtype).max
    fImg = rImg/maxV
    fImg = amplify_shades_fimg(fImg, bBoostAmplify)
    rImg = numpy.round(fImg*maxV).astype(rImg.dtype)
    return rImg


def handle_args(args, cfg=gCfg, cb=None):
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
    print(cfg)
    return cfg


def init(cfg):
    """
    Update the internal gCfg dictionary with the key-value pairs in passed cfg dictionary.
    """
    global gCfg
    for k in cfg:
        gCfg[k] = cfg[k]
    return gCfg


if __name__ == "__main__":
    print("ImgUtils: use this as a module")

