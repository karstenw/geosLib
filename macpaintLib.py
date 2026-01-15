
# -*- coding: utf-8 -*-

import sys
import os

import datetime
import struct

import zipfile
import gzip

import unicodedata

import PIL
import PIL.Image
import PIL.ImageDraw

# import cStringIO

import pprint
pp = pprint.pprint

import pdb
kwdbg = 0
kwlog = 0

import time

#
# constants
#

# to be filled out
quickdraw1Colors = {}

pictPrefix = chr(0) * 512


#
# tools
#
def datestring(dt = None, dateonly=False, nospaces=False):
    if not dt:
        now = str(datetime.datetime.now())
    else:
        now = str(dt)
    if not dateonly:
        now = now[:19]
    else:
        now = now[:10]
    if nospaces:
        now = now.replace(" ", "_")
    return now

def makeunicode( s, enc="utf-8", normalizer='NFC'):
    try:
        if type(s) != unicode:
            s = unicode(s, enc)
    except:
        pass
    s = unicodedata.normalize(normalizer, s)
    return s

def iterateFolders( infolder, validExtensions=False ):
    """Iterator that walks a folder and returns all files."""
    
    # for folder in dirs:
    lastfolder = ""
    for root, dirs, files in os.walk( infolder ):
        root = makeunicode( root )
        result = {}
        pathlist = []
        
        for thefile in files:
            thefile = makeunicode( thefile )
            basename, ext = os.path.splitext(thefile)
            
            typ = ext.lower()

            if thefile.startswith('.'):
                continue

            filepath = os.path.join( root, thefile )
            dummy, folder = os.path.split( root )
            if kwdbg or 1:
                if root != lastfolder:
                    lastfolder = root
                    print(  )
                    print( "FOLDER:", repr( root ) )
            filepath = makeunicode( filepath )
            
            if 0:
                if typ not in validExtensions:
                    # check for cvt file by scanning
                    f = open(filepath, 'rb')
                    data = f.read(4096)
                    f.close()
                    format = data[0x1e:0x3a]

                    formatOK = False
                    if format.startswith( b"PRG formatted GEOS file"):
                        formatOK = True
                    elif format.startswith( b"SEQ formatted GEOS file"):
                        broken = True

                    if not formatOK:
                        continue
                    typ = '.cvt'

            if kwlog and 1:
                print( "FILE:", filepath )
            yield typ, filepath

def getCompressedFile( path, acceptedOnly=False ):
    """Open a gzip or zip compressed file. Return the GEOS and c64 files in
    contained disk image(s)
    
    """
    result = {}

    # limit size of files to 10MB
    # use a size limit?
    if 0: #s.st_size > 10*2**20:
        s = os.stat( path )
        return result

    folder, filename = os.path.split( path )
    basename, ext = os.path.splitext( filename )

    if ext.lower() == '.gz':
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
    elif ext.lower() == '.zip':
        foldername = basename + '_zip'
        try:
            handle = zipfile.ZipFile(path, 'r')
            files = handle.infolist()
        except Exception as err:
            print( "ZIP ERROR", err )
            return result

        for zf in files:
            print( "ZIPFILE:", zf.filename  )
            try:
                h = handle.open(zf)
                data = h.read()
            except Exception as err:
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

class ImageBuffer(list):
    """For debugging purposes mostly. Has a built in memory dump in
    monitor format."""
    def __init__(self):
        super(ImageBuffer, self).__init__()
    def dump(self):
        hexdump( self )

def hexdump( s, col=32 ):
    """Using this for debugging was so memory lane..."""

    cols = {
         8: ( 7, 0xfffffff8),
        16: (15, 0xfffffff0),
        32: (31, 0xffffffe0),
        64: (63, 0xffffffc0)}

    if not col in cols:
        col = 16
    minorMask, majorMask = cols.get(col)
    d = False
    mask = col-1
    if type(s) in( list, tuple, bytes, bytearray): #ImageBuffer):
        d = True
    for i,c in enumerate(s):
        if d:
            t = hex(c)[2:]
        else:
            t = hex(ord(c))[2:]
        t = t.rjust(2, '0')

        # spit out address
        if i % col == 0:
            a = hex(i)[2:]
            a = a.rjust(4,'0')
            sys.stdout.write(a+':  ')
        sys.stdout.write(t+' ')

        # spit out ascii line
        if i & minorMask == minorMask:
            offs = i & majorMask
            
            for j in range(col):
                c2 = s[offs+j]
                if d:
                    d2 = chr(c2)
                else:
                    d2 = c2
                if 32 <= c2 < 127:
                    sys.stdout.write( d2 )
                else:
                    sys.stdout.write( '.' )
            sys.stdout.write('\n')
    sys.stdout.write('\n')
    sys.stdout.flush()


#
# file tools
#

#
# macpaint image conversion
#


def unpackBits( s ):
    
    resultBytes = bytearray(0)
    
    # 72 bytes times 720 lines
    totalBytes = 72 * 720 #len(resultBytes)
    byteIndex = 0
    
    done = False
    
    # check for header
    # Before extracting the image data from a MacPaint file in a non-Macintosh
    # environment, you must determine if a MacBinary header is prepended. This is best
    # done by reading the bytes at offsets 101 through 125 and checking to see if they
    # are all zero. The byte at offset 2 should be in the range of 1 to 63, and the DWORDs
    # at offsets 83 and 87 should be in the range of 0 to 007FFFFFh. If all of these
    # checks are true, then a MacBinary header is present.
    
    # check 1 bytes[101:126] are zero
    
    # check 2 byte[2] in range( 1,63 )
    
    # check 3 
    
    s = s[640:]
    totalBytes = len( s )
    # pdb.set_trace()
    
    def handleOpcode( data, idx ):
        op = data[idx]
    
    
    while ( byteIndex < totalBytes and not done):
        try:
            c = s[byteIndex]
            byteIndex += 1
        except Exception as err:
            print()
            print(err)
            print( "1 byteIndex >= totalBytes", byteIndex, totalBytes )
            done = True
            break
        co = c
        
        # print( hex(co) )
        
        if co < 128:
            #print( "POSITIVE OPCODE", hex(co) )
            debugList = [co]
            for i in range( co+1 ):
                # c = f.read(1); q = f.tell()
                try:
                    c = s[byteIndex]
                    byteIndex += 1
                except Exception as err:
                    print()
                    print(err)
                    print( "2 byteIndex >= totalBytes", byteIndex, totalBytes )
                    done = True
                    break
                resultBytes.append( c )
                debugList.append( c )
            #hexdump( debugList )
        else:
            #print( "NEGATIVE OPCODE", hex(co) )
            debugList = [co]
            co -= 256
            co = -co
            try:
                c = s[byteIndex]
                byteIndex += 1
            except Exception as err:
                print()
                print(err)
                print( "3 byteIndex >= totalBytes", byteIndex, totalBytes )
                done = True
                break
            for i in range(co+1):
                resultBytes.append( c )
                debugList.append( c )
            #hexdump( debugList )
    return resultBytes


def imageband2PNG( imageBytes, cardsw, h):
    """Convert a list of expanded imageBytes bytes into a PNG.
    
    """
    cardsh = h >> 3
    if h & 7 != 0:
        cardsh += 1
    w = cardsw * 8

    noofcards = cardsw * cardsh
    noofbytes = cardsw * h
    
    # check sizes
    n = len(imageBytes)
    expectedSize = noofbytes
    
    # repair section
    if n < expectedSize:
        # actual bits missing
        # fill with 0
        if kwlog or 1:
            print( "BITMAP BITS MISSING", expectedSize - n )
            
        # fill bitmap up
        imageBytes.extend( [0] * (expectedSize - n) )
        n = len(imageBytes)

    elif n == noofbytes:
        # everything's ok
        if kwlog:
            print( "BITMAP OK" )

    elif n > noofbytes:
        if kwlog or 1:
            print( "BITMAP TOO BIG", n )
        imageBytes = imageBytes[:noofbytes]
        n = len(imageBytes)

    # invert bw bitmap
    # looks better most of the cases
    bwbytes = [ i ^ 255 for i in imageBytes]

    # for the bitmap image
    #bwbytes = ''.join( bwbytes )
    bwimg = PIL.Image.frombytes('1', (w,h), bytes(bwbytes), decoder_name='raw')

    return bwimg


if __name__ == '__main__':
    for input in sys.argv[1:]:
        path = os.path.abspath( os.path.expanduser( input ))
        folder, filename = os.path.split( path )
        basename, ext = os.path.splitext( filename )

        if os.path.isdir( path ):
            
            files = iterateFolders( path )
        else:
            files = ( (ext.lower(), path), )
    
    for typ,path in files:
        f = open(path, 'rb')
        s = f.read()
        f.close()
        # pdb.set_trace()
        folder, filename = os.path.split( path )
        basename, ext = os.path.splitext( filename )
        
        dest = os.path.abspath( "./macpaintExports/" )
        if not os.path.exists( dest ):
            os.makedirs( dest )
        dest = os.path.join( dest, basename + ".png")

        if s.startswith( bytes( (0,0,0,2) ) ): #(chr(0),chr(0),chr(0),chr(2)) ):
            s = s[640:]
        
        if typ in (".mac", ".mpnt", ".pnt", ".pntg", ".pic"):
            print( path )
            image = unpackBits( s )
            img = imageband2PNG( image, 72, 720)
            img.save( dest )

