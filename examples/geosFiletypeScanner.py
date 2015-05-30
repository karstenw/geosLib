
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
GEOSDirEntry = geosLib.GEOSDirEntry
GEOSHeaderBlock = geosLib.GEOSHeaderBlock
VLIRFile = geosLib.VLIRFile
CBMConvertFile = geosLib.CBMConvertFile
hexdump = geosLib.hexdump
DiskImage = geosLib.DiskImage
imagesizeToExt = geosLib.imagesizeToExt
filetypesWithAuthor = geosLib.filetypesWithAuthor
programTypes = geosLib.programTypes

makeunicode = geosLib.makeunicode
getCompressedFile = geosLib.getCompressedFile
iterateFolders = geosLib.iterateFolders


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

        # pdb.set_trace()

        f = os.path.abspath(os.path.expanduser(f))
        folder, filename = os.path.split( f )
        basename, ext = os.path.splitext( filename )

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
                    for item in data:
                        result.append( item )

            elif typ == '.cvt':
                # pdb.set_trace()
                data = CBMConvertFile( path )
                result.append( data.vlir )
                cvtfiles += 1

            elif typ in ('.d64', '.d81'):
                images += 1
                data = DiskImage( filepath=path )
                result.extend( data.files )

            else:
                pass
            
            # pdb.set_trace()

            for cbmfile in result:
                totalCBMFiles += 1
                #if path not in fileTree:
                #    fileTree[path] = []
                
                #fileTree[path].append( cbmfile )
                try:
                    gde = cbmfile.dirEntry
                except AttributeError, err:
                    print err
                    pdb.set_trace()
                    print 

                # print directory entry
                gde.smallprnt()

                if cbmfile.header == "":
                    continue

                if gde.isGEOSFile:
                    gfh = cbmfile.header
                    #try:
                    #    gfh.prnt()
                    #except AttributeError, err:
                    #    print err
                    #    pdb.set_trace()
                    #    print 
                    # hexdump(gfh.rawdata, 32)
                    gfh = cbmfile.header
                    geosClasses.add( gfh.className )
                    if gfh.geosFileType in programTypes:
                        # pdb.set_trace()
                        geosApplications.add(gde.fileName)
                        a = gfh.author
                        a = a.strip( geosLib.stripchars )
                        a = a.strip( '\r\n \t' )
                        a = a.replace( chr(0xa0), ' ')
                        a = a.replace( chr(0x00), '_')
                        geosAuthors.add( a )
    print "\n" * 2
    print "Authors"
    pp(geosAuthors)
    
    print "\n" * 2
    print "Applications"
    pp(geosApplications)
    
    print "\n" * 2
    print "Classes"
    pp(geosClasses)

    print
    print "totalCBMFiles:", totalCBMFiles
    print
    print "images:", images
    print
    print "cvtfiles:", cvtfiles
    print
    print "compressedImages:", compressedImages
