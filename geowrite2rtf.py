
# -*- coding: utf-8 -*-


import sys
import os

import struct

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

import geoPaint
photoScrap = geoPaint.photoScrap

SUPPRESS_NUL = False
FF_TO_LF = False

import PIL
import PIL.Image
import PIL.ImageDraw


class ItemCollector(object):
    """Collect the rtf, html and image snippets for second pass assembly.
    """
    def __init__(self):
        self.textcollection = []
        self.htmlcollection = []
        self.rtfcollection = []
        self.imagecollection = {}
    def addHTML(self, s):
        self.htmlcollection.append(s)
    def addRTF(self, s):
        self.rtfcollection.append(s)
    def addTEXT(self, s):
        self.textcollection.append(s)
    def addImage(self, name, w, h, img):
        self.imagecollection[name] = (w,h,img)
    



def main():
    for f in sys.argv[1:]:
        
        infile = os.path.abspath(os.path.expanduser(f))
        folder, filename = os.path.split( infile )
        
        basename, ext = os.path.splitext( filename )
        
        gpf = CBMConvertFile( infile )
        gde = gpf.geosDirEntry


        print_html = 1
        print_rtf = 1
    
        ic = ItemCollector()
        ic.addRTF( "{\\rtf1 " )

        log = []
        # geowrite
        chains = gpf.vlir.chains
        for idx,chain in enumerate(chains):
            # pdb.set_trace()
            if chain in ( (0,0), (0,255), None, False):
                continue

            if idx >= 61:
                break

            style = 0
            font_size = 0
            font_id = 0
            n = len(chain)
            j = -1
            while j < n-1:
                j += 1
                dist = n - j
                if dist <= 2:
                    # pdb.set_trace()
                    pass
                c = chain[j]
                nc = ord(c)

                if nc == 0:
                    if j == 0:
                        if kwlog:
                            print "<<<Unknown Escape 0x00>>>"
                        j += 19
                        log.append("0x00 at start")
                        continue
                    if SUPPRESS_NUL:
                        continue

                elif nc == 12:
                    if FF_TO_LF:
                        ic.addRTF( "\n\n" )
                        ic.addHTML( "<br/><br/>\n" )
                        ic.addTEXT( "\n\n" )
                        continue
                    else:
                        ic.addRTF( "\\page " )
                        ic.addTEXT( c )
                        ic.addHTML( "<hr/>\n" )
                        log.append("LF")
                        continue

                elif nc == 13:
                    ic.addRTF( "\\\n" )
                    ic.addHTML( "<br/>\n" )
                    ic.addTEXT( "\n" )
                    log.append("RET")
                    continue;

                elif nc == 16:
                    # graphics escape
                
                    width = ord(chain[j+1]) * 8
                    heightL = ord(chain[j+2])
                    heightH = ord(chain[j+3])
                    height = heightH * 256 + heightL
                    chainindex = ord(chain[j+4])

                    # pdb.set_trace()
                    if  63 <= chainindex <= 127:
                        # pdb.set_trace()
                        # width, height, image = photoScrap( chains[chainindex] )
                        colimg, bwimg = photoScrap( chains[chainindex] )
                        image = colimg
                        if not (width and height and image):
                            j += 4
                            continue
                        imagename = str(chainindex).rjust(5, '0') + ".png"
                        # image.save(imagename)
                        rtfs = "{{\\NeXTGraphic %s \\width%i \\height%i} " + chr(0xac) + "}"
                        ic.addRTF( rtfs % (imagename, width, height) )
                        ic.addHTML( '<img src="%s" />' % (imagename,) )
                        ic.addTEXT( "\n\nIMAGEFILE(%i, %i, %s)\n\n" % (width, height, imagename) )
                        ic.addImage( imagename, width, height, image )

                    else:
                        pdb.set_trace()
                        print "INDEX ERROR"

                    if kwlog:
                        print "<<<Graphics Escape>>> %i:%i @ VLIR:%i" % (width, height, chainindex)

                    j += 4
                    log.append("GRPHX vlir:%i, w: %i, h: %i" % (chainindex,width,height) )
                    continue

                elif nc == 17:
                    # ruler escape
                    leftMargin = struct.unpack("<H", chain[j+1:j+3])[0]
                    rightMargin = struct.unpack("<H", chain[j+3:j+5])[0]

                    s1 = j+5
                    s2 = j+7
                    dec = 2**15
                    tabs = []
                    for i in range(8):
                        tab = struct.unpack("<H", chain[s1:s2])[0]
                        if tab & dec:
                            tab -= dec
                            tabs.append( (tab, 1) )
                        else:
                            tabs.append( (tab, 0) )
                        s1 += 2
                        s2 += 2

                    paragraphMargin = struct.unpack("<H", chain[j+21:j+23])[0]

                    justifiation = ord( chain[j+23] ) & 3

                    spacing = ord( chain[j+23] ) >> 2 & 3
                
                    color = ord( chain[j+24] )
                
                    justifications = {
                        0:  'left',
                        1:  'center',
                        2:  'right',
                        3:  'justify'}
                    spacings = {
                        0: "\\sl240 ",
                        1: "\\sl360 ",
                        2: "\\sl480 "}

                    ic.addRTF( spacings.get(spacing, "") )
                    ic.addRTF( "\\q%s " % (justifications[justifiation],) )

                    ic.addHTML( '<span align="%s">' % (justifications[justifiation],) )

                    if kwlog:
                        print "leftmargin:", repr(leftMargin)
                        print "rightMargin:", repr(rightMargin)
                        print "paragraphMargin:", repr(paragraphMargin)
                        print "justifiation:", repr(justifiation)
                        print "spacing:", repr(spacing)
                        print "color:", repr(color)
                        print "tabs:", tabs
                
                    for tab in tabs:
                        tabpoint, decimal = tab
                        if tabpoint >= rightMargin:
                            continue
                        if decimal:
                            ic.addRTF( "\\tqdec" )
                        ic.addRTF( "\\tx%i" % (tabpoint * 20) )

                    j += 26
                    log.append("RULER")
                    continue

                elif nc == 23:
                    # NEWCARDSET
                    fontL = ord(chain[j+1])
                    fontH = ord(chain[j+2])
                    newfont = fontH * 256 + fontL
                    fontid = newfont >> 5
                    fontsize = newfont & 0x1f
                    newstyle = ord(chain[j+3])
                
                    if kwlog:
                        print "segment:", repr(chain[j:j+4])
                        print "<<<NEWCARDSET Escape>>>"
                        print "fontID:", fontid
                        print "font size:", fontsize
                        print "style:", bin(style)
                
                    if fontid != font_id:
                        font_id = fontid

                    if fontsize != font_size:
                        ic.addHTML( '<span style="font-size: %ipt">'  % fontsize )
                        ic.addRTF( "\\fs%i " % (fontsize * 2,) )
                        font_size = fontsize

                    if style != newstyle:
                        if 0: #newstyle & 7 != 0:
                            pdb.set_trace()
                        bits = [2**i for i in range(1,8)]
                        stylecodes = ['sub','sup','out','ita','rev','bld','uln']
                        rtfcommands = (
                            ('\\nosupersub ', '\\sub '),
                            ('\\nosupersub ', '\\super '),
                            ('\\outl0\\strokewidth0 ', '\\outl\\strokewidth60 '),
                            ('\\i0 ', '\\i '),
                            ('{\\colortbl;\\red0\\green0\\blue0;\\red255\\green255\\blue255;}\\cb1\\cf2 ',
                             '{\\colortbl;\\red0\\green0\\blue0;\\red255\\green255\\blue255;}\\cb2\\cf1 '),
                            ('\\b0 ', '\\b '),
                            ('\\ulnone ', '\\ul '))

                        rtfstyles = dict(zip(bits, rtfcommands))
                        if kwdbg:
                            print "oldstyle", bin(style)
                            print "newstyle", bin(newstyle)
                        # pdb.set_trace()

                        for bit in bits:
                            curr = newstyle & bit
                            old = style & bit
                    
                            if       curr and     old:
                                # no change
                                pass
                            elif not curr and not old:
                                # no change
                                pass
                            elif     curr and not old:
                                # switch on
                                ic.addRTF( rtfstyles[bit][1] )
                            elif not curr and     old:
                                # switch off
                                ic.addRTF( rtfstyles[bit][0] )
                        style = newstyle
                    log.append("NEWCARDSET")
                    j += 3
                    continue
                elif nc == 8 or c == 24:
                    j += 19
                    bytes = [hex(ord(i)) for i in chain[j:j+10]]
                    pp(bytes)
                    # pdb.set_trace()
                    log.append("0x08 | 0x24")
                    continue
                elif nc == 0xf5:
                    j += 10
                    log.append("0xF5")
                    continue
                elif c in ('{','}'):
                    ic.addRTF( "\\%s" % c )
                    ic.addHTML( c )
                    ic.addTEXT( c )
                    log.append("{}")
                    continue

                ic.addRTF( c )
                ic.addHTML( c )
                ic.addTEXT( c )
                if log:
                    if log[-1] != "CHARS":
                        log.append("CHARS")

            if kwlog:
                print "<<<New Page>>>"

        ic.addRTF( "}" )
        # f.close()
        # write out files

        # pdb.set_trace()
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
    main()



