
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

import geosData
geoPaintBand = geosData.geoPaintBand
photoScrap = geosData.photoScrap

# it seems the "official" geoColorChoice is fg: color0, bg: color15

bgcol = c64colors[15]
if kwdbg:
    bgcol = c64colors[14]

# make a white bands for empty records
bytes = [ chr(bgcol[0]),chr(bgcol[1]),chr(bgcol[2]) ] * (640*16)
bytes = ''.join( bytes )
coldummy = PIL.Image.frombytes('RGB', (640,16), bytes, decoder_name='raw')

bytes = [ chr(255) ] * 1280
bytes = ''.join( bytes )
bwdummy = PIL.Image.frombytes('1', (640,16), bytes, decoder_name='raw')



def convertGeoPaintFile( infile, gpf, gdh):
    outnamebase = gde.fileName
    outnamebase = outnamebase.replace(":", "_")
    outnamebase = outnamebase.replace("/", "_")
    folder = gpf.folder
    print repr(outnamebase)

    colimg = PIL.Image.new('RGB', (80*8,90*8), 1)
    bwimg = PIL.Image.new('1', (80*8,90*8), 1)
    # pdb.set_trace()

    version = 1
    if gdh.classNameString == "Paint Image V1.0":
        version = 1
    chains = gpf.vlir.chains
    for i,chain in enumerate(chains):
        if chain == (0,0):
            break
        if chain == (0,255):
            #print "EMPTY BAND!"
            col, bw = coldummy.copy(), bwdummy.copy()
        else:
            col, bw = geoPaintBand( chain, version )
        if not col:
            # print "NO BAND!"
            col = coldummy.copy()
        colimg.paste( col, (0,i*16,640,(i+1)*16))
        if not bw:
            bw = bwdummy.copy()
        bwimg.paste( bw, (0,i*16,640,(i+1)*16))

    outfilecol = os.path.join( folder, outnamebase + "_col.png" )
    outfilebw = os.path.join( folder, outnamebase + "_bw.png" )
    colimg.save(outfilecol)
    bwimg.save(outfilebw)

def convertPhotoAlbumFile( f, gpf, gdh):
    
    outnamebase = gde.fileName
    outnamebase = outnamebase.replace(":", "_")
    outnamebase = outnamebase.replace("/", "_")
    folder = gpf.folder
    print repr(outnamebase)


    chains = gpf.vlir.chains
    
    # extract clip names for Photo Album V2.1
    clipnames = [ "" ] * 127
    clipnameschain = 256
    if gdh.classNameString == "photo album V2.1":
        # scan for last chain
        if (0,0) in chains:
            clipnameschain = chains.index( (0,0) ) - 1
            clipnamesstream = chains[clipnameschain]
            noofentries = ord(clipnamesstream[0])
            for i in range(noofentries):
                base = 1 + i*17
                namebytes = clipnamesstream[base:base+16]
                namebytes = namebytes.replace( chr(0x00), "" )
                namebytes = namebytes.replace( '/', "-" )
                namebytes = namebytes.replace( ':', "_" )
                clipnames[i] = namebytes
    
    for i,chain in enumerate(chains):
        if chain in ((0,0), (0,255), None, False):
            continue
        if i == clipnameschain:
            # names record
            continue

        col, bw = photoScrap( chain )
        
        clipname = ""
        if clipnames[i]:
            clipname = '-"' + clipnames[i] + '"'
        if col:
            suf = '-' + str(i+1).rjust(3,'0') + clipname + "_col.png"
            of = os.path.join( folder, outnamebase + suf )
            col.save( of )
        else:
            print "No color image for vlir: %i" % i
        if bw:
            suf = '-' + str(i+1).rjust(3,'0') + clipname + "_bw.png"
            of = os.path.join( folder, outnamebase + suf )
            bw.save( of )
        else:
            print "No bw image for vlir: %i" % i
            


def convertPhotoScrapFile( f, gpf, gdh):
    if kwlog:
        print "convertPhotoScrapFile( f, gpf, gdh)"
    
    outnamebase = gde.fileName
    outnamebase = outnamebase.replace(":", "_")
    outnamebase = outnamebase.replace("/", "_")
    folder = gpf.folder
    print repr(outnamebase)

    chains = gpf.vlir.chains
    for i,chain in enumerate(chains):
        if chain == (0,0):
            break
        if chain == (0,255):
            continue

        col, bw = photoScrap( chain )

        if col:
            suf = '-' + str(i+1).rjust(3,'0') + "_col.png"
            of = os.path.join( folder, outnamebase + suf )
            col.save( of )
        if bw:
            suf = '-' + str(i+1).rjust(3,'0') + "_bw.png"
            of = os.path.join( folder, outnamebase + suf )
            bw.save( of )


if __name__ == '__main__':
    # pdb.set_trace()
    for f in sys.argv[1:]:
        
        f = os.path.abspath(os.path.expanduser(f))
        folder, filename = os.path.split( f )
        
        gpf = CBMConvertFile( f )
        gde = gpf.geosDirEntry

        if kwdbg and 0:
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

        gdh = gpf.vlir.header

        # print file info
        print 
        print 'X' * 80
        print repr(f)
        gde.prnt()
        print "----"

        if gdh.classNameString.startswith("Paint Image V"):
            gdh.prnt()
            print '-' * 80
            convertGeoPaintFile( f, gpf, gdh)
        elif gdh.classNameString.startswith("photo album V"):
            # pdb.set_trace()
            gdh.prnt()
            print '-' * 80
            convertPhotoAlbumFile( f, gpf, gdh)
        elif gdh.classNameString.startswith("Photo Scrap V"):
            gdh.prnt()
            print '-' * 80
            convertPhotoScrapFile( f, gpf, gdh)
        else:
            print
            print "NOT PROCESSED:", repr(f)
            print "Class:", repr(gdh.classNameString)
            print '#' * 80
            print
