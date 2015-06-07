
# -*- coding: utf-8 -*-


import sys
import os

import struct
import gzip, zipfile

import unicodedata

import pdb
kwdbg = 0
kwlog = 0

import pprint
pp = pprint.pprint

import geosLib
geosLib.kwdbg = kwdbg
geosLib.kwdbg = kwdbg

GEOSDirEntry = geosLib.GEOSDirEntry
GEOSHeaderBlock = geosLib.GEOSHeaderBlock
VLIRFile = geosLib.VLIRFile
CBMConvertFile = geosLib.CBMConvertFile
hexdump = geosLib.hexdump
DiskImage = geosLib.DiskImage
imagesizeToExt = geosLib.imagesizeToExt
filetypesWithAuthor = geosLib.filetypesWithAuthor
programTypes = geosLib.programTypes

convertGeoPaintFile = geosLib.convertGeoPaintFile
convertPhotoScrapFile = geosLib.convertPhotoScrapFile
convertPhotoAlbumFile = geosLib.convertPhotoAlbumFile
convertWriteImage = geosLib.convertWriteImage
acceptedTypes = geosLib.acceptedTypes
textTypes = geosLib.textTypes

makeunicode = geosLib.makeunicode
iterateFolders = geosLib.iterateFolders
getCompressedFile = geosLib.getCompressedFile

convertFontFile = geosLib.convertFontFile

exportFolder = os.path.abspath( "./geosFonts" )
if not os.path.exists( exportFolder ):
    os.makedirs( exportFolder ) 


if __name__ == '__main__':

    geosClasses = set()
    geosApplications = set()
    geosAuthors = set()
    
    images = 0
    cvtfiles = 0
    compressedImages = 0
    
    totalCBMFiles = 0
    
    fileTree = {}

    for f in sys.argv[1:]:

        f = os.path.abspath(os.path.expanduser(f))
        folder, filename = os.path.split( f )
        basename, ext = os.path.splitext( filename )
        dummy, parentFolder = os.path.split( folder )

        print "\n\n\n"
        print "#" * 120
        print "SOURCE:", repr(f)
        print "#" * 120

        
        if os.path.isdir(f):
            files = iterateFolders( f )
        else:
            # make a file behave like it came from the iterator
            typ = ext.lower()
            files = [ (typ,f) ]

        for typ, path in files:

            result = []
            if typ in ('.gz', '.zip'):
                # perhaps compressed image
                data = getCompressedFile(path)
                if data:
                    compressedImages += 1
                    result.append( data )
                    #for item in data:
                    #    result.append( {'': item} )

            elif typ == '.cvt':
                # pdb.set_trace()
                data = CBMConvertFile( path )
                d = {'': [data.vlir]}
                result.append( d )
                cvtfiles += 1

            elif typ in ('.d64', '.d81'):
                images += 1
                data = DiskImage( filepath=path )
                # pdb.set_trace()
                n = basename + typ.replace('.', '_')
                d = {n: []}
                for u in data.files:
                    if u.header and u.header.className in acceptedTypes:
                        d[n].append( u )
                result.append( d )
            else:
                pass

            for item in result:
                for fld in item:
                    for cbmfile in item[fld]:
                        try:
                            gde = cbmfile.dirEntry
                        except AttributeError, err:
                            print err
                            print 
                        gde.smallprnt()

                        if cbmfile.header == "":
                            continue

                        if gde.isGEOSFile:
                            gfh = cbmfile.header
                            if gfh.geosFileType == 8:
                                convertFontFile(cbmfile, exportFolder)
                                if False and kwlog:
                                    gfh.prnt()
                                    print '-' * 80
