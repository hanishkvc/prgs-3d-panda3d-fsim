#!/usr/bin/env python3
# Color a Grayscale image based on color at corresponding location in a reference image
# The grayscale and reference images need to be GeoTiff images.
# The Color image generated will be a png.
# This can be used to color say a heightfield image based on World Vegetation NDVI data
# HanishKVC, 2021
# GPL


import sys
import imgutils as iu


def run_main():
    imgRef = iu.GTImage(gCfg['sFNameRef'], "REF")
    imgRef.print_info()
    imgSrc = iu.GTImage(gCfg['sFNameSrc'], "SRC")
    imgSrc.print_info()

    rCM = iu.map_gray2color_gti(imgSrc, imgRef)
    fnCM = "{}.cm.png".format(imgSrc.fName)
    iu.save(fnCM, rCM)


if __name__ == "__main__":
    gCfg = iu.handle_args(sys.argv)
    run_main()

