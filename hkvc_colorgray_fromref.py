#!/usr/bin/env python3
# Color a Grayscale image based on color at corresponding location in a reference image
# The grayscale and reference images need to be GeoTiff images.
# The Color image generated will be a png.
# This can be used to color say a heightfield image based on World Vegetation NDVI data
# HanishKVC, 2021
# GPL


import sys
import imgutils as iu


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
            'bFlip': True,
            'bFlipVert': True,
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
    imgRef = iu.GTImage(gCfg['refFName'], "REF")
    imgRef.print_info()
    imgSrc = iu.GTImage(gCfg['srcFName'], "Src")
    imgSrc.print_info()

    rCM = iu.map_gray2color(imgSrc, imgRef)
    fnCM = "{}.cm.png".format(imgSrc.fName)
    iu.GTImage.Save(fnCM, rCM)


if __name__ == "__main__":
    gCfg = handle_args(sys.argv)
    iu.init(gCfg)
    run_main()

