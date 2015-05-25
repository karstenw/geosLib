
# -*- coding: utf-8 -*-


import sys
import os

import struct

import PIL
import PIL.Image
import PIL.ImageDraw

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
VLIRFile = c64Data.VLIRFile
CBMConvertFile = c64Data.CBMConvertFile
hexdump = c64Data.hexdump
DiskImage = c64Data.DiskImage 

import geosData
geoPaintBand = geosData.geoPaintBand
photoScrap = geosData.photoScrap
convertGeoPaintFile = geosData.convertGeoPaintFile
convertPhotoAlbumFile = geosData.convertPhotoAlbumFile
convertPhotoScrapFile = geosData.convertPhotoScrapFile




if __name__ == '__main__':
    # pdb.set_trace()
    for f in sys.argv[1:]:
        
        f = os.path.abspath(os.path.expanduser(f))
        folder, filename = os.path.split( f )
        
        gpf = CBMConvertFile( f )

        # old debug vlir export
        if 0:
            for i,c in enumerate(gpf.vlir.chains):
                if c == (0,0):
                    break
                if c == (0,255):
                    continue
                cnum = '-' + str(i).rjust(3, '0')
                outpath = os.path.join(folder, filename + cnum)
                out = open(outpath, 'wb')
                out.write( c )
                out.close()

        vlir = gpf.vlir
        gdh = gpf.vlir.header

        if kwdbg:
            # print file info
            print 
            print 'X' * 80
            print repr(f)
            gde = gpf.geosDirEntry
            gde.prnt()
            print "----"

        if vlir.header.className.startswith("Paint Image V"):
            if kwdbg:
                vlir.header.prnt()
                print '-' * 80
            convertGeoPaintFile( vlir, folder )
        elif vlir.header.className.startswith("photo album V"):
            if kwdbg:
                vlir.header.prnt()
                print '-' * 80
            convertPhotoAlbumFile( vlir, folder )
        elif vlir.header.className.startswith("Photo Scrap V"):
            if kwdbg:
                vlir.header.prnt()
                print '-' * 80
            convertPhotoScrapFile( vlir, folder )
        else:
            print
            print "NOT PROCESSED:", repr(f)
            print "Class:", repr(vlir.header.className)
            print '#' * 80
            print
