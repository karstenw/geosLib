
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


if __name__ == '__main__':
    # make an image with the c64 colors
    import PIL
    import PIL.Image
    import PIL.ImageDraw

    c = 256
    d = c >> 2
    c64colrect = PIL.Image.new('RGB', (c,c), (1,1,1))
    draw = PIL.ImageDraw.Draw( c64colrect )
    for y in range(4):
        for x in range(4):
            col = y * 4 + x
            xc = x * d
            yc = y * d
            col = geosLib.c64colors[col]
            draw.rectangle((xc,yc,xc+d,yc+d), fill=col, outline=None)
        
    c64colrect.save("C64 colors.png")
