
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
geosLib.kwlog = kwlog

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

exportFolder = os.path.abspath("./geosExports")
fontExportFolder = os.path.abspath("./geosFonts")


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

        basefolder = os.path.join( exportFolder, parentFolder )

        print "\n\n\n"
        print "#" * 120
        print 
        print "SOURCE:", repr(f)
        print "-" * 120
        print

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

            elif typ in ('.d64', '.d81'):
                images += 1
                data = DiskImage( filepath=path )
                # pdb.set_trace()
                n = basename + typ.replace('.', '_')
                d = {n: []}
                for u in data.files:
                    if u.header:
                        if u.header.className in acceptedTypes:
                            d[n].append( u )
                        elif u.dirEntry.geosFileType == 8:
                            d[n].append( u )
                result.append( d )
            else:
                # elif typ == '.cvt':
                # pdb.set_trace()
                #data = CBMConvertFile( path )
                #d = {'': [data.vlir]}
                #result.append( d )
                #cvtfiles += 1
                # elif typ == '.seq':
                # pdb.set_trace()
                data = CBMConvertFile( path )
                d = {'': [data.vlir]}
                result.append( d )
                cvtfiles += 1
                # check for cvt without extension here
                # check sda, arc, ark...
                # pass

            for item in result:
                for fld in item:
                    for cbmfile in item[fld]:
                        if kwdbg or 1:
                            print cbmfile.dirEntry.fileName
                            # pdb.set_trace()
                            print
                        try:
                            gde = cbmfile.dirEntry
                        except AttributeError, err:
                            print err
                            # pdb.set_trace()
                            print 
                        gde.smallprnt()

                        if cbmfile.header == "":
                            continue

                        if gde.isGEOSFile:
                            gfh = cbmfile.header
                            target = os.path.join( basefolder, fld)
                            target = basefolder

                            done = False

                            if gfh.className.startswith("Paint Image V"):
                                convertGeoPaintFile( cbmfile, target )
                                done = True
                            elif gfh.className.startswith("photo album V"):
                                convertPhotoAlbumFile( cbmfile, target )
                                done = True
                            elif gfh.className.startswith("Photo Scrap V"):
                                convertPhotoScrapFile( cbmfile, target )
                                done = True
                            elif gfh.className in textTypes:
                                convertWriteImage( cbmfile, target )
                                done = True

                            elif gfh.geosFileType == 8:
                                # font file
                                # ATTENTION: exports all in one folder!
                                convertFontFile(cbmfile, fontExportFolder)
                                done = True

                            if done and kwlog:
                                gde.prnt()
                                gfh.prnt()
                                print '-' * 80
