#!/usr/bin/env python
#coding=utf-8

__author__ = 'WD'

import sys
import os
from PIL import Image

def Main():
    argvLen = len(sys.argv)

    if argvLen < 2:
        print "argv len less than 2"
        return

    sourceIconPath = sys.argv[1]

    if not os.path.exists(sourceIconPath):
        print "image not exist in:" + sourceIconPath
        return

    img = Image.open(sourceIconPath)
    srcWidth, srcHeight = img.size
    targetWidthArray = (29,29,40,50,57,58,58,60,72,76,80,80,87,100,114,120,120,144,152)
    targetNameArray = ("UI_ICON_29-1.png",
                       "UI_ICON_29.png",
                       "UI_ICON_40.png",
                       "UI_ICON_50.png",
                       "UI_ICON_57.png",
                       "UI_ICON_58-1.png",
                       "UI_ICON_58.png",
                       "UI_ICON_60.png",
                       "UI_ICON_72.png",
                       "UI_ICON_76.png",
                       "UI_ICON_80-1.png",
                       "UI_ICON_80.png",
                       "UI_ICON_87.png",
                       "UI_ICON_100.png",
                       "UI_ICON_114.png",
                       "UI_ICON_120-1.png",
                       "UI_ICON_120.png",
                       "UI_ICON_144.png",
                       "UI_ICON_152.png")

    for i in range(0, len(targetWidthArray)):
        targetImg = img.resize(
            (targetWidthArray[i], targetWidthArray[i] * srcHeight / srcWidth),
            Image.ANTIALIAS)

        newFilePath = os.path.dirname(sourceIconPath)
        targetImg.save(newFilePath + os.sep + targetNameArray[i], 'png')
        print newFilePath + os.sep + targetNameArray[i]

    return

if __name__ == '__main__':
    Main()

