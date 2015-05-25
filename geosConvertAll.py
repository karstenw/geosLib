
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

import c64Data
GEOSDirEntry = c64Data.GEOSDirEntry
GEOSHeaderBlock = c64Data.GEOSHeaderBlock
VLIRFile = c64Data.VLIRFile
CBMConvertFile = c64Data.CBMConvertFile
hexdump = c64Data.hexdump
DiskImage = c64Data.DiskImage
imagesizeToExt = c64Data.imagesizeToExt
filetypesWithAuthor = c64Data.filetypesWithAuthor
programTypes = c64Data.programTypes


import geosData
convertGeoPaintFile = geosData.convertGeoPaintFile
convertPhotoScrapFile = geosData.convertPhotoScrapFile
convertPhotoAlbumFile = geosData.convertPhotoAlbumFile
convertWriteImage = geosData.convertWriteImage
acceptedTypes = geosData.acceptedTypes
textTypes = geosData.textTypes



def makeunicode( s, enc="utf-8", normalizer='NFC'):
    try:
        if type(s) != unicode:
            s = unicode(s, enc)
    except:
        pass
    s = unicodedata.normalize(normalizer, s)
    return s

def getCompressedFile( path, typ, acceptedOnly=False ):

    result = {}
    # limit size of files to 10MB
    s = os.stat( path )
    if 0: #s.st_size > 10*2**20:
        return result

    folder, filename = os.path.split( path )
    basename, ext = os.path.splitext( filename )

    if typ == '.gz':
        f = gzip.open(path, 'rb')
        foldername = basename + '_gz'
        result[foldername] = []
        file_content = f.read()
        f.close()
        # only return those streams that have a chance of being an image
        if len(file_content) in imagesizeToExt:
            di = DiskImage( stream=file_content, tag=path )
            if acceptedOnly:
                for u in di.files:
                    if u.header.className in acceptedTypes:
                        result[foldername].append( u )
            else:
                result[foldername].extend(di.files)
            return result
    elif typ == '.zip':
        foldername = basename + '_zip'
        try:
            handle = zipfile.ZipFile(path, 'r')
            files = handle.infolist()
        except Exception, err:
            print "ZIP ERROR", err
            return result

        for zf in files:
            print "ZIPFILE:", repr( zf.filename )
            try:
                h = handle.open(zf)
                data = h.read()
            except Exception, err:
                continue
            if len(data) in imagesizeToExt:
                zfoldername = '/'.join( (foldername, zf.filename) )
                result[zfoldername] = []
                # pdb.set_trace()
                di = DiskImage( stream=data, tag=path )
                if acceptedOnly:
                    for u in di.files:
                        if u.header.className in acceptedTypes:
                            result[zfoldername].append( u )
                else:
                    result[zfoldername].extend( di.files )
        return result
    return result


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
        dummy, parentFolder = os.path.split( folder )

        basefolder = os.path.abspath(os.path.expanduser("./geosExports"))
        basefolder = os.path.join( basefolder, parentFolder )

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
                            pdb.set_trace()
                            print 
                        gde.smallprnt()

                        if cbmfile.header == "":
                            continue

                        if gde.isGEOSFile:
                            gfh = cbmfile.header
                            target = os.path.join( basefolder, fld)
                            if not os.path.exists( target ):
                                os.makedirs( target) 
                            if gfh.className.startswith("Paint Image V"):
                                if kwdbg:
                                    gfh.prnt()
                                    print '-' * 80
                                # pdb.set_trace()
                                convertGeoPaintFile( cbmfile, target )
                            elif gfh.className.startswith("photo album V"):
                                if kwdbg:
                                    gfh.prnt()
                                    print '-' * 80
                                convertPhotoAlbumFile( cbmfile, target )
                            elif gfh.className.startswith("Photo Scrap V"):
                                if kwdbg:
                                    gfh.prnt()
                                    print '-' * 80
                                convertPhotoScrapFile( cbmfile, target )
                            elif gfh.className in textTypes:
                                if kwdbg:
                                    gfh.prnt()
                                    print '-' * 80
                                convertWriteImage( cbmfile, target )
                        
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
