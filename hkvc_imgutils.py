#!/usr/bin/env python3
# Allow few different operations on images.
# Option1: Color a Grayscale image based on color at corresponding location in a reference image
#   The grayscale and reference images need to be GeoTiff images.
#   The Color image generated will be a png.
#   This can be used to color say a heightfield image based on World Vegetation NDVI data
# Option2: Reduce the color resolution / shades in a image
#   This can be used to reduce the amount of detail in a heightfield to some extent.
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


def run_main():
    try:
        if gCfg['sCmd'] == "gray2color":
            run_gray2color()
        elif gCfg['sCmd'] == "reduceshades":
            run_reduceshades()
    except:
        print(sys.exc_info())
        print("thisPrg --sCmd gray2color --sFNameSrc <srcImage> --sFNameRef <refImage>")
        print("thisPrg --sCmd reduceshades --sFNameSrc <srcImage>")


if __name__ == "__main__":
    gCfg = iu.handle_args(sys.argv)
    run_main()

