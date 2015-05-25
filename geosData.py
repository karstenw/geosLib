
# -*- coding: utf-8 -*-


import sys
import os

import struct

import PIL
import PIL.Image
import PIL.ImageDraw

import c64Data
hexdump = c64Data.hexdump
ImageBuffer = c64Data.ImageBuffer
c64colors = c64Data.c64colors

import pdb
kwdbg = 0
kwlog = 0

import pprint
pp = pprint.pprint


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



def expandImageStream( s ):
    n = len(s)
    j = -1
    image = ImageBuffer()
    
    log = []
    while j < n-1:
        j += 1
        code = ord(s[j])
        items = []
        roomleft = (n-1) - j
        if 0: #code == 0:
            break
        if code in (64, 128):
            if kwdbg:
                print "blank code 64,128 encountered."
                pdb.set_trace()
            continue

        if code < 64:
            if roomleft < 1:
                j += 1
                continue
            data = s[j+1:j+code+1]
            for i in data:
                items.append( ord(i) )
            j += len(data)
            image.extend( items )
            continue

        elif 64 <= code < 128:
            if roomleft < 8:
                j += 8
                continue
            c = code & 63
            pattern = s[j+1:j+9]
            pn = len(pattern)
            cnt = pn * c
            for i in range(c):
                for k in range(pn):
                    p = pattern[k]
                    items.append( ord(p) )
            j += pn
            image.extend( items )
            continue

        elif 128 <= code:
            if roomleft < 1:
                j += 1
                continue
            c = code - 128
            data = ord(s[j+1])
            t = [data] * c
            items = t
            image.extend( items )
            j += 1
            continue

        if kwdbg:
            log.append( items )
    return image


def expandScrapStream( s ):
    n = len(s)
    j = -1
    image = []
    while j < n-1:
        j += 1
        code = ord(s[j])
        roomleft = (n-1) - j
        if code in (0,128,220):
            if kwdbg:
                print "ILLEGAL OPCODES..."
                pdb.set_trace()
                print
            continue
        elif code < 128:
            if roomleft < 1:
                j += 1
                continue
            data = ord(s[j+1])
            t = [data] * code
            image.extend( t )
            j += 1
            continue
        elif 128 <= code <= 219:
            c = code - 128
            if roomleft < c:
                j += c
                continue
            data = s[j+1:j+c+1]
            for i in data:
                image.append( ord(i) )
            j += c
            continue
            
        else:
            # 220...255
            patsize = code -220
            if roomleft < patsize+1:
                j += patsize+1
                continue
            repeat = ord(s[j+1])
            size = repeat * patsize
            pattern = s[j+2:j+2+patsize]
            for i in range( repeat ):
                for p in pattern:
                    image.append( ord(p) )
            
            j += patsize+1
            continue
    return image


def photoScrap( s ):
    if s in ( None, (0,255), (0,0)):
        return
    
    # check for name list in Photo Album V2.1
    cnt = ord(s[0])
    n = len(s)
    
    # this is now handled in Album code
    #if n == (((cnt + 1) * 17) + 1):
    #    # skip it
    #    hexdump(s)
    #    return 0,0    
    cardsw = ord(s[0])
    w = cardsw * 8
    h = ord(s[2]) * 256 + ord(s[1])
    cardsh = h >> 3
    image = expandScrapStream(s[3:])
    if image:
        col, bw = imageband2PNG( image, cardsw, cardsh, 0 )
        return col, bw
    return False, False


def geoPaintBand( s ):
    if s in ( None, (0,255), (0,0)):
        return False, False
    cardsw = 80
    cardsh = 2
    image = expandImageStream(s)
    col, bw = imageband2PNG( image, cardsw, cardsh, 1 )
    if kwdbg and 0:
        col.save("lastband_col.png")
        bw.save("lastband_bw.png")
    return col, bw


def imageband2PNG( image, cardsw, cardsh, isGeoPaint):
    w = cardsw * 8
    h = cardsh * 8

    eightZeroBytes = [0] * 8

    noofcards = cardsw * cardsh
    noofbytes = noofcards * 8
    
    noofcolorbands = cardsh
    
    # holds a list of card colors; one list per row
    colorbands = []
    
    # pdb.set_trace()

    # check sizes
    n = len(image)
    bitmapsize = cardsw * h
    colormapsize = noofcards
    gap = 8
    expectedSize = bitmapsize + gap + colormapsize
    
    # repair section
    if n < bitmapsize:
        # actual bits missing
        # fill with 0
        # one colored image
        if kwdbg:
            pdb.set_trace()
            print "BITMAP BITS MISSING", bitmapsize - n
            
        # fill bitmap up
        image.extend( [0] * (bitmapsize - n) )
        
        # add gap
        image.extend( [0] * 8 )
        
        # add color map
        image.extend( [191] * colormapsize )

        n = len(image)

    elif n == bitmapsize:
        # one colored image
        if kwdbg:
            print "ONLY BITMAP BITS"
        # add gap
        image.extend( [0] * 8 )
        
        # add color map
        image.extend( [191] * colormapsize )

        n = len(image)

    elif n == bitmapsize + colormapsize:
        # colored image not created by geoPaint (I guess)
        if kwdbg:
            #pdb.set_trace()
            print "COLOR GAP MISSING"
        i0 = image[:bitmapsize]
        c0 = image[bitmapsize:]
        image = []
        image.extend( i0 )
        image.extend( [0] * 8 )
        image.extend( c0 )
        n = len(image)

    elif n == expectedSize:
        # should be all ok and parts sitting where they're expected to be
        pass
    else:
        # TBD
        # Here is still work todo
        if n > expectedSize:
            i0 = image[:bitmapsize]
            c0 = image[-colormapsize:]
            legap = image[bitmapsize:-colormapsize]
            #pdb.set_trace()
            #hexdump( legap )
            image = []
            image.extend( i0 )
            image.extend( [0] * 8 )
            image.extend( c0 )
            n = len(image)
        else:
            if kwdbg:
                print  
                print  "UNUSUAL SIZE!!"
                print cardsw, cardsh
                print cardsw * cardsh
                print n
                print expectedSize
                print

    # extract color data
    offset = cardsw * h + 8
    for row in range(cardsh):
        base = offset + row * cardsw
        end = base + cardsw
        band = image[base:end]
        if len(band) < cardsw:
            if kwdbg:
                print "color band extend", (cardsw -len(band))
            band.extend( [191] * (cardsw -len(band)) )
        colorbands.append( band )

    
    if isGeoPaint:
        bytes = [ chr(0) ] * noofbytes
        # this is only for geoPaint files
        ROWS = cardsh
        COLS = cardsw
        BYTESPERCARD = 8
        BYTESPERROW = COLS * BYTESPERCARD

        idx = -1
        for row in range(ROWS):
            for col in range(COLS):
                for byte in range(BYTESPERCARD):
                    idx += 1
                    src = 0 + (BYTESPERROW * row) + col * BYTESPERCARD + byte
                    # 0-15 
                    base = row * BYTESPERCARD 
                    dst = base * 80 + byte * 80 + col
                    # dst = base * cardsw + byte * cardsw + col
                    try:
                        byte = image[idx]
                    except IndexError:
                        byte = 0

                    if dst >= noofbytes:
                        pdb.set_trace()
                        print row
                        print col
                        print byte
                        print row * BYTESPERCARD 
                    bytes[dst] = byte
    else:
        # scraps are easy
        bytes = image[:]

    # separate 
    colbytes = [chr(i) for i in bytes]

    # invert bw bitmap
    # looks better most of the cases
    bwbytes = [chr(i ^ 255) for i in bytes]

    # for the bitmap image
    bwbytes = ''.join( bwbytes )
    bwimg = PIL.Image.frombytes('1', (w,h), bwbytes, decoder_name='raw')

    # a bw source for the color image; cards get copied in bw mode
    colbytes = ''.join(colbytes)
    colsource = PIL.Image.frombytes('1', (w,h), colbytes, decoder_name='raw')

    # new image
    colimg = PIL.Image.new('RGB', (w,h), (1,1,1))

    for row in range(cardsh):
        # create the color image by
        # 1. painting background color 8x8 cards (draw.rectangle below)
        # 2. drawing the cards foreground data in bw with fg coloring (draw.bitmap)
        base = row * cardsw
        for col in range(cardsw):
            idx = base + col

            color = colorbands[row][col]
            bgi = color & 15
            bg = c64colors[bgi]
            fgi = (color >> 4) & 15
            fg = c64colors[fgi]

            draw = PIL.ImageDraw.Draw( colimg )

            # get coordinates for copy/paste
            x = col * 8
            y = row * 8

            # fill the card with background color
            draw.rectangle( (x,y,x+8,y+8), fill=bg)

            # copy the bitmap data
            bwcard = colsource.crop( (x,y,x+8,y+8) )
            bwcard.load()
            card = bwcard.copy()

            # paste the bw bitmap into a color imaga, coloring the card
            draw.bitmap( (x,y), card, fill=fg)

    return (colimg, bwimg)


def convertGeoPaintFile( vlir, folder ):
    # gpf, gdh
    outnamebase = vlir.dirEntry.fileName
    outnamebase = outnamebase.replace(":", "_")
    outnamebase = outnamebase.replace("/", "_")
    if kwdbg:
        print repr(outnamebase)

    colimg = PIL.Image.new('RGB', (80*8,90*8), 1)
    bwimg = PIL.Image.new('1', (80*8,90*8), 1)
    # pdb.set_trace()

    for i,chain in enumerate(vlir.chains):
        if chain == (0,0):
            break
        if chain == (0,255):
            #print "EMPTY BAND!"
            col, bw = coldummy.copy(), bwdummy.copy()
        else:
            col, bw = geoPaintBand( chain )
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


def convertPhotoAlbumFile( vlir, folder ):
    # f, gpf
    outnamebase = vlir.dirEntry.fileName
    outnamebase = outnamebase.replace(":", "_")
    outnamebase = outnamebase.replace("/", "_")
    # folder = gpf.folder
    print repr(outnamebase)

    # extract clip names for Photo Album V2.1
    clipnames = [ "" ] * 127
    clipnameschain = 256
    if vlir.header.className == "photo album V2.1":
        # scan for last chain
        if (0,0) in vlir.chains:
            clipnameschain = vlir.chains.index( (0,0) ) - 1
            clipnamesstream = vlir.chains[clipnameschain]
            noofentries = ord(clipnamesstream[0])
            for i in range(noofentries):
                base = 1 + i*17
                namebytes = clipnamesstream[base:base+16]
                namebytes = namebytes.replace( chr(0x00), "" )
                namebytes = namebytes.replace( '/', "-" )
                namebytes = namebytes.replace( ':', "_" )
                clipnames[i] = namebytes
    
    for i,chain in enumerate(vlir.chains):
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
            


def convertPhotoScrapFile( vlir, folder):
    # f, gpf, gdh
    if kwlog:
        print "convertPhotoScrapFile( f, gpf, gdh)"
    
    outnamebase = vlir.dirEntry.fileName
    outnamebase = outnamebase.replace(":", "_")
    outnamebase = outnamebase.replace("/", "_")
    # folder = gpf.folder
    print repr(outnamebase)

    for i,chain in enumerate(vlir.chains):
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


class ItemCollector(object):
    """Collect the rtf, html and image snippets for second pass assembly.
    """
    def __init__(self):
        self.textcollection = []
        self.htmlcollection = []
        self.rtfcollection = [ ]
        self.imagecollection = {}

        
    def initDoc(self, title):
        self.addRTF( "{\\rtf1 " )
        self.addHTML( "<!DOCTYPE html><html><head><title>%s</title></head><body>" % title )
    
    def finishDoc( self, s=""):
        self.addHTML( "</body></html>" )
        self.addRTF( "}" )
    
    def addHTML(self, s):
        self.htmlcollection.append(s)
    def addRTF(self, s):
        self.rtfcollection.append(s)
    def addTEXT(self, s):
        self.textcollection.append(s)
    def addImage(self, name, w, h, img):
        self.imagecollection[name] = (w,h,img)


# make this work on VLIRFile + index
def getGeoWriteStream(items, chain, chains, log, flags):
    """Decode a geoWrite Stream; usually a page of a document.
    
    IN: items   - collector for RTF, HTML and TXT snippets
        chain   - the stream to decode
        chains  - the whole vlir object. Needed for image reference
    """

    SUPPRESS_NUL, FF_TO_LF = flags
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
                items.addRTF( "\n\n" )
                items.addHTML( "<br/><br/>\n" )
                items.addTEXT( "\n\n" )
                continue
            else:
                items.addRTF( "\\page " )
                items.addTEXT( c )
                items.addHTML( "<hr/>\n" )
                log.append("LF")
                continue

        elif nc == 13:
            items.addRTF( "\\\n" )
            items.addHTML( "<br/>\n" )
            items.addTEXT( "\n" )
            log.append("RET")
            continue;

        elif nc == 16:
            # graphics escape
    
            width = ord(chain[j+1]) * 8
            heightL = ord(chain[j+2])
            heightH = ord(chain[j+3])
            height = heightH * 256 + heightL
            chainindex = ord(chain[j+4])

            if 63 <= chainindex <= 127:
                colimg, bwimg = photoScrap( chains[chainindex] )
                image = colimg
                if not (width and height and image):
                    j += 4
                    continue
                imagename = str(chainindex).rjust(5, '0') + ".png"
                # image.save(imagename)
                rtfs = "{{\\NeXTGraphic %s \\width%i \\height%i} " + chr(0xac) + "}"
                items.addRTF( rtfs % (imagename, width, height) )
                items.addHTML( '<img src="%s" />' % (imagename,) )
                items.addTEXT( "\n\nIMAGEFILE(%i, %i, %s)\n\n" % (width, height, imagename) )
                items.addImage( imagename, width, height, image )

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

            items.addRTF( spacings.get(spacing, "") )
            items.addRTF( "\\q%s " % (justifications[justifiation],) )

            items.addHTML( '<span align="%s">' % (justifications[justifiation],) )

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
                    items.addRTF( "\\tqdec" )
                items.addRTF( "\\tx%i" % (tabpoint * 20) )

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
                items.addHTML( '<span style="font-size: %ipt">'  % fontsize )
                items.addRTF( "\\fs%i " % (fontsize * 2,) )
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
                        items.addRTF( rtfstyles[bit][1] )
                    elif not curr and     old:
                        # switch off
                        items.addRTF( rtfstyles[bit][0] )
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
            items.addRTF( "\\%s" % c )
            items.addHTML( c )
            items.addTEXT( c )
            log.append("{}")
            continue

        items.addRTF( c )
        items.addHTML( c )
        items.addTEXT( c )
        if log:
            if log[-1] != "CHARS":
                log.append("CHARS")

    if kwlog:
        print "<<<New Page>>>"
    
    return items, log


def convertTextDoc( vlir, folder, flags ):

    # prepare
    log = []
    basename = vlir.dirEntry.fileName
    ic = ItemCollector()
    ic.initDoc( basename )
    chains = vlir.chains

    
    # page loop
    for idx,chain in enumerate(chains):
        # pdb.set_trace()
        if chain in ( (0,0), (0,255), None, False):
            continue

        if idx >= 61:
            break

        ic, log = getGeoWriteStream(ic, chain, chains, log, flags)

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

