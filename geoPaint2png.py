
# -*- coding: utf-8 -*-


import sys
import os

import struct

import PIL
import PIL.Image
import PIL.ImageDraw

import pdb
kwdbg = True
kwlog = True

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

import geoPaint
geoPaintBand = geoPaint.geoPaintBand
photoScrap = geoPaint.photoScrap


# make a white bands for empty records
bytes = [ chr(255),chr(255),chr(255) ] * (640*16)
bytes = ''.join( bytes )
coldummy = PIL.Image.frombytes('RGB', (640,16), bytes, decoder_name='raw')

bytes = [ chr(255) ] * 1280
bytes = ''.join( bytes )
bwdummy = PIL.Image.frombytes('1', (640,16), bytes, decoder_name='raw')



def convertGeoPaint( infile, gpf, gdh):
    outnamebase = gde.fileName
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

def convertPhotoAlbum( f, gpf, gdh):
    
    outnamebase = gde.fileName
    folder = gpf.folder
    print repr(outnamebase)


    version = 1
    if gdh.classNameString == "photo album V2.1":
        # currently not doable
        return 
    chains = gpf.vlir.chains
    for i,chain in enumerate(chains):
        if chain == (0,0):
            break
        if chain == (0,255):
            #print "EMPTY BAND!"
            continue
        else:
            col, bw = photoScrap( chain )
            # pdb.set_trace()
            if col:
                suf = str(i+1).rjust(3,'0') + "_col.png"
                of = os.path.join( folder, outnamebase + suf )
                col.save( of )
            if bw:
                suf = str(i+1).rjust(3,'0') + "_bw.png"
                of = os.path.join( folder, outnamebase + suf )
                bw.save( of )

def convertPhotoScrap( f, gpf, gdh):
    pass


if __name__ == '__main__':
    # pdb.set_trace()
    for f in sys.argv[1:]:
        
        gpf = CBMConvertFile( f )
        gde = gpf.geosDirEntry
        # currently only vlir files
        if gde.geosFileStructureString != "VLIR":
            continue
        gdh = gpf.vlir.header

        # print file info
        print '-' * 80
        gde.prnt()
        print '-' * 40
        gdh.prnt()
        print '-' * 80

        if gdh.classNameString.startswith("Paint Image V"):
            convertGeoPaint( f, gpf, gdh)
        elif gdh.classNameString.startswith("photo album V"):
            convertPhotoAlbum( f, gpf, gdh)
        elif gdh.classNameString.startswith("Photo Scrap V"):
            convertPhotoScrap( f, gpf, gdh)
        else:
            print
            print "NOT PROCESSED!"
            print '#' * 80
            print
