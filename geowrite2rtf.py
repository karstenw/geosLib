
# -*- coding: utf-8 -*-


import sys
import os

import pdb
kwdbg = 0
kwlog = 0

import pprint
pp = pprint.pprint

import c64Data
fontmapping = c64Data.fontmapping
c64colors = c64Data.c64colors
GEOSDirEntry = c64Data.GEOSDirEntry
GEOSHeaderBlock = c64Data.GEOSHeaderBlock
CBMConvertFile = c64Data.CBMConvertFile

import geosData
convertWriteImage = geosData.convertWriteImage

SUPPRESS_NUL = False
FF_TO_LF = False

import PIL
import PIL.Image
import PIL.ImageDraw



def convertWriteDocument( f ):
    
    infile = os.path.abspath(os.path.expanduser(f))
    folder, filename = os.path.split( infile )
    
    basename, ext = os.path.splitext( filename )
    
    gpf = CBMConvertFile( infile )
    gde = gpf.geosDirEntry
    gdh = gpf.vlir.header

    if kwdbg:
        print '-' * 20
        print gde.fileName
        print gdh.className
    if gdh.className not in (
                "Write Image V1.0",
                "Write Image V1.1",
                "Write Image V2.0",
                "Write Image V2.1",
                "text album  V1.0",
                'text album  V1.0',
                'text album  V2.1',
                "text album  V2.1",
                "Text  Scrap V1.0",
                "Text  Scrap V1.1",
                "Text  Scrap V2.0",
                "Text  Scrap V2.1"):
        print "IGNORED:", repr( infile )
        return ""

    convertWriteImage( gpf.vlir, folder, (SUPPRESS_NUL, FF_TO_LF) )
    
if __name__ == '__main__':
    for f in sys.argv[1:]:
        convertWriteDocument( f )



