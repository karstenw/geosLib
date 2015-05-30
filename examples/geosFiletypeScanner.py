
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


def makeunicode( s, enc="utf-8", normalizer='NFC'):
    try:
        if type(s) != unicode:
            s = unicode(s, enc)
    except:
        pass
    s = unicodedata.normalize(normalizer, s)
    return s

def getCompressedFile( path, typ ):
    # limit size of files to 10MB
    s = os.stat( path )
    if s.st_size > 10*2**20:
        return []
    if typ == '.gz':
        f = gzip.open(path, 'rb')
        file_content = f.read()
        f.close()
        # only return those streams that have a chance of being an image
        if len(file_content) in imagesizeToExt:
            di = DiskImage( stream=file_content, tag=path )
            return di.files
    elif typ == '.zip':
        try:
            handle = zipfile.ZipFile(path, 'r')
            files = handle.infolist()
        except Exception, err:
            print "ZIP ERROR", err
            return []
        result = []
        for zf in files:
            print "ZIPFILE:", repr( zf.filename )
            try:
                h = handle.open(zf)
                data = h.read()
            except Exception, err:
                continue
            if len(data) in imagesizeToExt:
                # pdb.set_trace()
                di = DiskImage( stream=data, tag=path )
                result.extend( di.files )
        return result
    return []


def iterateFolders( infolder, validExtensions=('.d64', '.d81', '.zip', '.gz', '.cvt') ):
    """Iterator that walks a folder and returns all files."""
    
    # for folder in dirs:
    for root, dirs, files in os.walk( infolder ):
        root = makeunicode( root )
        result = {}
        pathlist = []

        for thefile in files:
            thefile = makeunicode( thefile )
            basename, ext = os.path.splitext(thefile)
            
            typ = ext.lower()
            if typ not in validExtensions:
                continue

            if thefile.startswith('.'):
                continue
            
            filepath = os.path.join( root, thefile )
            filepath = makeunicode( filepath )
            yield typ, filepath


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
                data = getCompressedFile(path, typ)
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
                        geosAuthors.add( gfh.author )
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
