
# -*- coding: utf-8 -*-


import sys
import os

import pdb
kwdbg = 0
kwlog = 0

import pprint
pp = pprint.pprint

import PIL
import PIL.Image
import PIL.ImageDraw

import c64Data
hexdump = c64Data.hexdump
ImageBuffer = c64Data.ImageBuffer
c64colors = c64Data.c64colors

def expandImageStream( s ):
    n = len(s)
    j = -1
    image = ImageBuffer()
    
    log = []
    while j < n-1:
        j += 1
        code = ord(s[j])
        items = []
        if 0: #code == 0:
            while len(image) < 1448:
                image.append( 0 )
            break
        if code in (64, 128):
            if kwdbg:
                print "blank code 64,128 encountered."
                pdb.set_trace()

        if code < 64:
            data = s[j+1:j+code+1]
            for i in data:
                items.append( ord(i) )
            j += len(data)
            image.extend( items )

        elif 64 <= code < 128:
            
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

        elif 128 <= code:
            c = code - 128
            data = ord(s[j+1])
            t = [data] * c
            items = t
            image.extend( items )
            j += 1

        log.append( items )
    return image


def expandScrapStream( s ):
    n = len(s)
    j = -1
    image = []
    while j < n-1:
        j += 1
        code = ord(s[j])
        
        if code in (0,128,220):
            continue
        elif code < 128:
            data = ord(s[j+1])
            t = [data] * code
            image.extend( t )
            j += 1
            continue
        elif 128 <= code <= 219:
            c = code - 128
            data = s[j+1:j+c+1]
            for i in data:
                image.append( ord(i) )
            j += c
            continue
            
        else:
            # 220...255
            patsize = code -220
            repeat = ord(s[j+1])
            size = repeat * patsize
            pattern = s[j+2:j+2+patsize]
            for i in range( repeat ):
                for p in pattern:
                    image.append( ord(p) )
            
            j += patsize + 1
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


def geoPaintBand( s, version ):
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
        print  
        if kwdbg:
            pdb.set_trace()
        print  "UNUSUAL SIZE!!"
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
