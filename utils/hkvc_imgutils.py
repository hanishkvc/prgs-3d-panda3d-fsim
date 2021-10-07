#!/usr/bin/env python3
# Allow few different operations on images.
# Option1: Color a Grayscale image based on color at corresponding location in a reference image
#   The grayscale and reference images need to be GeoTiff images.
#   The Color image generated will be a png.
#   This can be used to color say a heightfield image based on World Vegetation NDVI data
# Option2: Reduce the color resolution / shades in a image
#   This can be used to reduce the amount of detail in a heightfield to some extent.
# Option3: Generate a Panda3D compatible heightfield png, from given heightfield image.
#   One could give a GeoTiff image containing elevation as input for example.
#   Note: The logic accepts elevation/heightfield/grayscale data in any file format.
# Option4: Generate Panda3D compatible heightfield and colormap images in one go.
#   One could give a GeoTiff image containing elevation as input for example.
# HanishKVC, 2021
# GPL
#


import sys
import imgutils as iu


def run_gray2color():
    imgRef = iu.GTImage(gCfg['sFNameRef'], "REF")
    imgRef.print_info()
    imgSrc = iu.GTImage(gCfg['sFNameSrc'], "SRC")
    imgSrc.print_info()

    rCM = iu.map_gray2color_gti(imgSrc, imgRef)
    fnCM = "{}.cm.png".format(imgSrc.fName)
    iu.save_rimg(fnCM, rCM, bTranspose=True)


def run_reduceshades():
    i1 = iu.load_rimg(gCfg['sFNameSrc'])
    #i2 = iu.reduce_shades_crude_rimg(i1,4,8)
    i2 = iu.reduce_shades_crude_rimg(i1,4,2)
    fnRS = "{}.rs.png".format(gCfg['sFNameSrc'])
    iu.save_rimg(fnRS, i2)


def run_p3dhf(bTranspose=False):
    iI = iu.load_rimg(gCfg['sFNameSrc'], bTranspose=bTranspose)
    iA = iu.amplify_shades_rimg(iI)
    iR = iu.resize_pwrof2square_rimg(iA,1)
    fnHF = "{}.hf.png".format(gCfg['sFNameSrc'])
    iu.save_rimg(fnHF, iR, bTranspose=bTranspose)
    return iR


def run_hf2cm(iI=None, bTranspose=True):
    if type(iI) == type(None):
        iI = iu.load_rimg(gCfg['sFNameSrc'], bTranspose=bTranspose)
    iC = iu.hf2cm_rimg(iI)
    iF = iu.flip_rimg(iC)
    fnCM = "{}.cm.png".format(gCfg['sFNameSrc'])
    iu.save_rimg(fnCM, iF, bTranspose=bTranspose)


def run_main():
    breakpoint()
    try:
        if gCfg['sCmd'] == "gray2color":
            run_gray2color()
        elif gCfg['sCmd'] == "reduceshades":
            run_reduceshades()
        elif gCfg['sCmd'] == "p3dhf":
            run_p3dhf()
        elif gCfg['sCmd'] == "hf2cm":
            run_hf2cm()
        elif gCfg['sCmd'] == "p3dterrain":
            iR = run_p3dhf(True)
            run_hf2cm(iR, True)
    except:
        print(sys.exc_info())
        print("thisPrg --sCmd gray2color --sFNameSrc <srcImage> --sFNameRef <refImage>")
        print("thisPrg --sCmd reduceshades --sFNameSrc <srcImage>")
        print("thisPrg --sCmd p3dhf --sFNameSrc <srcImage>")
        print("thisPrg --sCmd hf2cm --sFNameSrc <srcImage>")
        print("thisPrg --sCmd p3dterrain --sFNameSrc <srcImage>")


if __name__ == "__main__":
    gCfg = iu.handle_args(sys.argv)
    run_main()

