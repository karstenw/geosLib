
# -*- coding: utf-8 -*-


import sys
import os

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
CBMConvertFile = c64Data.CBMConvertFile

import geosData
photoScrap = geosData.photoScrap
ItemCollector = geosData.ItemCollector
getGeoWriteStream = geosData.getGeoWriteStream

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
    print '-' * 20
    print gde.fileName
    print gdh.className
    if gdh.className not in (
                "Write Image V1.0",
                "Write Image V1.1",
                "Write Image V2.0",
                "Write Image V2.1",
                "text album  V1.0",
                "text album  V1.1",
                "text album  V2.0",
                "text album  V2.1",
                "Text  Scrap V1.0",
                "Text  Scrap V1.1",
                "Text  Scrap V2.0",
                "Text  Scrap V2.1"):
        print "IGNORED:", repr( infile )
        return ""

    # prepare
    log = []
    ic = ItemCollector()
    ic.initDoc( gde.fileName )
    chains = gpf.vlir.chains

    
    # page loop
    for idx,chain in enumerate(chains):
        # pdb.set_trace()
        if chain in ( (0,0), (0,255), None, False):
            continue

        if idx >= 61:
            break

        ic, log = getGeoWriteStream(ic, chain, chains, log, (SUPPRESS_NUL, FF_TO_LF))

    # finish doc
    ic.finishDoc()
    ic.addRTF( "}" )

    # write out
    rtfs = ''.join( ic.rtfcollection )
    htmls = ''.join( ic.htmlcollection )
    texts = ''.join( ic.textcollection )

    rtfoutfolder = os.path.join( folder, basename + ".rtfd" )
    if not os.path.exists( rtfoutfolder ):
        os.makedirs( rtfoutfolder )
    rtfoutfile = os.path.join( rtfoutfolder, "TXT.rtf")
    f = open(rtfoutfile, 'wb')
    f.write( rtfs )
    f.close()

    htmloutfolder = os.path.join( folder, basename + "_html" )
    if not os.path.exists( htmloutfolder ):
        os.makedirs( htmloutfolder )
    htmloutfile = os.path.join( htmloutfolder, "index.html")
    f = open(htmloutfile, 'wb')
    f.write( htmls )
    f.close()

    textoutfile = os.path.join(folder, basename + ".txt")
    f = open(textoutfile, 'wb')
    f.write( texts )
    f.close()

    # write images
    for filename in ic.imagecollection:
        w,h,img = ic.imagecollection[filename]
    
        rtfimage = os.path.join( rtfoutfolder, filename )
        htmlimage = os.path.join( htmloutfolder, filename )
        img.save( rtfimage )
        img.save( htmlimage )

if __name__ == '__main__':
    for f in sys.argv[1:]:
        convertWriteDocument( f )



