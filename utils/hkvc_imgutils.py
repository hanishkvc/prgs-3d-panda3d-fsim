#!/usr/bin/env python3
# Allow few different operations on images.
# Option1: Map a given image to represent the equivalent region in a given reference image.
#   The source and reference images need to be GeoTiff images.
#   The new image generated will be a png.
#   This can be used to color say a elevation/heightfield image based on WorldVegetation/NDVI data
# Option2: Reduce the color resolution / shades in a image
#   This can be used to reduce the amount of detail in a heightfield to some extent.
# Option3: Generate a Panda3D compatible heightfield png, from given heightfield image.
#   One could give a GeoTiff image containing elevation as input for example.
#   Note: The logic accepts elevation/heightfield/grayscale data in any file format.
# Option4: Generate Panda3D compatible heightfield and colormap images in one go.
#   One could give a GeoTiff image containing elevation as input for example.
# Option5: Map objects (rather airports) belonging to a given GeoTiff's region, into a text file.
# HanishKVC, 2021
# GPL
#


import sys
import numpy
import imgutils as iu
import odb


def run_mapto():
    imgRef = iu.GTImage(gCfg['sFNameRef'], "REF")
    imgRef.print_info()
    imgSrc = iu.GTImage(gCfg['sFNameSrc'], "SRC")
    imgSrc.print_info()

    rCM = iu.mapto_ex_gti(imgSrc, imgRef)
    fnCM = "{}.cm.png".format(imgSrc.fName)
    iu.save_rimg(fnCM, rCM, bTranspose=True)


def run_mapobjects():
    imgSrc = iu.GTImage(gCfg['sFNameSrc'], "SRC")
    imgSrc.print_info()
    db = odb.load(gCfg['sFNameODB'])
    ll = iu.map_objects_gti(imgSrc, db)
    fnObjs = "{}.objects".format(imgSrc.fName)
    f = open(fnObjs, "wt+")
    f.write("HDR1:SLon:{}:ELon:{}:SLat:{}:ELat:{}\n".format(imgSrc.sLon, imgSrc.eLon, imgSrc.sLat, imgSrc.eLat))
    f.write("HDR2:XWidth:{}:YHeight:{}\n".format(imgSrc.XW, imgSrc.YH))
    for l in ll:
        f.write("{}\n".format(l))


def run_reduceshades():
    i1 = iu.load_rimg(gCfg['sFNameSrc'])
    #i2 = iu.reduce_shades_crude_rimg(i1,4,8)
    i2 = iu.reduce_shades_crude_rimg(i1,4,2)
    fnRS = "{}.rs.png".format(gCfg['sFNameSrc'])
    iu.save_rimg(fnRS, i2)


def run_p3dhf(bTranspose=False):
    iI = iu.load_rimg(gCfg['sFNameSrc'], bTranspose=bTranspose)
    iA = iu.amplify_shades_fimg(iI, gCfg['bBoostAmplify'])
    numpy.save("/tmp/20A.npy", iA)
    iR = iu.resize_pwrof2square_rimg(iA,1, gCfg['iResizeFilter'])
    numpy.save("/tmp/20R.npy", iR)
    fnHF = "{}.hf.png".format(gCfg['sFNameSrc'])
    iu.save_rimg(fnHF, iR, bTranspose=bTranspose, bExpand=True)
    return iR


def run_hf2cm(iI=None, bTranspose=True):
    if type(iI) == type(None):
        iI = iu.load_rimg(gCfg['sFNameSrc'], bTranspose=bTranspose)
    iC = iu.hf2cm_rimg(iI)
    iF = iu.flip_rimg(iC)
    fnCM = "{}.cm.png".format(gCfg['sFNameSrc'])
    iu.save_rimg(fnCM, iF, bTranspose=bTranspose)


def run_lcrop():
    iI = iu.load_rimg(gCfg['sFNameSrc'], bTranspose=gCfg['bTranspose'])
    xS = gCfg['iXS']
    yS = gCfg['iYS']
    xE = gCfg['iXE']
    yE = gCfg['iYE']
    iC = iu.crop_rimg(iI, xS, yS, xE, yE)
    fnC = "{}.c.png".format(gCfg['sFNameSrc'])
    iu.save_rimg(fnC, iC, bTranspose=gCfg['bTranspose'])


def run_main():
    if type(gCfg.get('bBreakPoint')) != type(None):
        breakpoint()
    try:
        if gCfg['sCmd'] == "mapto":
            run_mapto()
        elif gCfg['sCmd'] == "mapobjects":
            run_mapobjects()
        elif gCfg['sCmd'] == "reduceshades":
            run_reduceshades()
        elif gCfg['sCmd'] == "p3dhf":
            run_p3dhf()
        elif gCfg['sCmd'] == "hf2cm":
            run_hf2cm()
        elif gCfg['sCmd'] == "p3dterrain":
            iR = run_p3dhf(True)
            run_hf2cm(iR, True)
        elif gCfg['sCmd'] == "lcrop":
            run_lcrop()
        else:
            raise RuntimeError("UnKnown Command:{}".format(gCfg['sCmd']))
    except:
        print(sys.exc_info())
        print("thisPrg --sCmd mapto --sFNameSrc <srcImage> --sFNameRef <refImage>")
        print("thisPrg --sCmd reduceshades --sFNameSrc <srcImage>")
        print("thisPrg --sCmd p3dhf --sFNameSrc <srcImage>")
        print("thisPrg --sCmd hf2cm --sFNameSrc <srcImage>")
        print("thisPrg --sCmd p3dterrain --sFNameSrc <srcImage>")
        print("thisPrg --sCmd lcrop --sFNameSrc <srcImage> --iXS <int> --iYS <int> --iXE <int> --iYE <int>")
        print("thisPrg --sCmd mapobjects --sFNameSrc <srcImage> --sFNameODB <odb.pickle>")


if __name__ == "__main__":
    gCfg = iu.handle_args(sys.argv)
    run_main()

