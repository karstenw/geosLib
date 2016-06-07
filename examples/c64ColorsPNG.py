
# -*- coding: utf-8 -*-

"""Create a PNG with the C64 colors."""



import sys
import os
import datetime
import struct

import pprint
pp = pprint.pprint


import pdb
kwdbg = 0
kwlog = 0

import geosLib

imagesize = 256

if __name__ == '__main__':
    # make an image with the c64 colors
    import PIL
    import PIL.Image
    import PIL.ImageDraw

    tilewidth = imagesize >> 2
    c64colrect = PIL.Image.new('RGB', (imagesize,imagesize), (1,1,1))
    draw = PIL.ImageDraw.Draw( c64colrect )
    for y in range(4):
        for x in range(4):
            col = y * 4 + x
            xc = x * tilewidth
            yc = y * tilewidth
            col = geosLib.c64colors[col]
            draw.rectangle((xc,yc,xc+tilewidth,yc+tilewidth), fill=col, outline=None)
        
    c64colrect.save("C64 colors.png")
