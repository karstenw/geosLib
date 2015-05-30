
# -*- coding: utf-8 -*-


import sys
import os

import pdb
kwdbg = 0
kwlog = 0

import pprint
pp = pprint.pprint

import geosLib
fontmapping = geosLib.fontmapping
c64colors = geosLib.c64colors
GEOSDirEntry = geosLib.GEOSDirEntry
GEOSHeaderBlock = geosLib.GEOSHeaderBlock
CBMConvertFile = geosLib.CBMConvertFile

convertWriteImage = geosLib.convertWriteImage

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
    if gdh.className not in geosLib.textTypes:
        print "IGNORED:", repr( infile )
        return ""

    convertWriteImage( gpf.vlir, folder, (SUPPRESS_NUL, FF_TO_LF), rtf=True )
    
if __name__ == '__main__':
    for f in sys.argv[1:]:
        convertWriteDocument( f )
