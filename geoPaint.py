
# -*- coding: utf-8 -*-


import sys
import os

import pdb
kwdbg = 0

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
        if 0: #code in (64, 128):
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
    if len(image) != 1448:
        #pdb.set_trace()
        #print "IMAGE SIZE MISMATCH!"
        #print len(image)
        # pp(log)
        pass
    return image

def expandImageStream_orig( s ):
    n = len(s)
    j = -1
    image = ImageBuffer()
    # pdb.set_trace()
    while j < n-1:
        j += 1
        code = ord(s[j])

        if code < 64:
            data = s[j+1:j+code+1]
            for i in data:
                image.append( ord(i) )
            j += code
            continue
        elif 64 <= code < 128:
            c = code & 63
            pattern = s[j+1:j+9]
            for i in range(c):
                a = j + 9 + i
                pa = a & 7
                image.append( ord(pattern[pa]) )
            j += (8 + c)

        elif 128 <= code:
            c = code - 128
            data = ord(s[j+1])
            t = [data] * c
            image.extend( t )
            j += 1
            continue
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
    cardsw = ord(s[0])
    w = cardsw * 8
    h = ord(s[2]) * 256 + ord(s[1])
    cardsh = h >> 3
    image = expandScrapStream(s[3:])
    if image:
        img = imageband2PNG( image, cardsw, cardsh, 1 )
        return img
    return False

def geoPaintBand( s, version ):
    if s in ( None, (0,255), (0,0)):
        return
    cardsw = 80
    cardsh = 2
    # pdb.set_trace()
    image = expandImageStream(s)
    if 1: #image and len(image)>= 1440:
        col, bw = imageband2PNG( image, cardsw, cardsh, version )
        if kwdbg:
            col.save("lastband_col.png")
            bw.save("lastband_bw.png")
        return col, bw
    return False

def imageband2PNG( image, cardsw, cardsh, version):
    w = cardsw * 8
    h = cardsh * 8
    noofcards = cardsw * cardsh
    colorbands = []
    
    # check sizes
    n = len(image)
    expectedSize = cardsw * h + noofcards + 8
    if n != expectedSize:
        # pdb.set_trace()
        print 
        print "SIZE MISMATCH!"
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
            band.extend( [1] * (cardsw -len(band)) )
        colorbands.append( band )

    bytes = [ chr(0) ] * 1280

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
                try:
                    byte = image[idx]
                except IndexError:
                    byte = 0
                bytes[dst] = byte

    # separate 
    colbytes = [chr(i) for i in bytes]

    # invert bw bytes. looks better most of the cases
    bwbytes = [chr(i ^ 255) for i in bytes]

    bwbytes = ''.join( bwbytes )
    bwimg = PIL.Image.frombytes('1', (w,h), bwbytes, decoder_name='raw')

    colbytes = ''.join(colbytes)
    colsource = PIL.Image.frombytes('1', (w,h), colbytes, decoder_name='raw')

    # new image
    colimg = PIL.Image.new('RGB', (w,h), (1,1,1))
    for row in range(cardsh):
        base = row * cardsw
        for col in range(cardsw):
            idx = base + col

            x = col * 8
            y = row * 8
            color = colorbands[row][col]
            bgi = color & 15
            bg = c64colors[bgi]
            fgi = (color >> 4) & 15
            fg = c64colors[fgi]

            draw = PIL.ImageDraw.Draw( colimg )
            draw.rectangle( (x,y,x+8,y+8), fill=bg)

            bwcard = colsource.crop( (x,y,x+8,y+8) )
            bwcard.load()
            draw.bitmap( (x,y), bwcard, fill=fg)
        return colimg, bwimg

    return (colimg, bwimg)
    # return bwimg




def photoScrap( s ):
    if s == None:
        return
    cardsw = ord(s[0])
    w = cardsw * 8
    h = ord(s[2]) * 256 + ord(s[1])
    cardsh = h >> 3
    noofcards = cardsw * cardsh
    image = []
    
    image = expandScrapStream(s[3:])

    # pdb.set_trace()

    colorbands = []
    # extract color data
    offset = cardsw * h
    for row in range(cardsh):
        base = offset + row * cardsw
        end = base + cardsw
        band = image[base:end]
        colorbands.append( band )

    # create bw image
    bwbytes = []
    colbytes = []
    for y in range(h):
        for x in range(cardsw):
            idx = y * cardsw + x
            cardbyte = image[idx]
            colbytes.append( chr(cardbyte) )
            cardbyte = cardbyte ^ 0xff
            bwbytes.append( chr(cardbyte) )

    bwbytes = ''.join( bwbytes )
    colbytes = ''.join( colbytes )

    bwimg = PIL.Image.frombytes('1', (w,h), bwbytes, decoder_name='raw')
    
    # stand in for color image - needs to be bw and not inverted
    colsource = PIL.Image.frombytes('1', (w,h), colbytes, decoder_name='raw')

    # create color image

    # new image
    colimg = PIL.Image.new('RGB', (w,h), 0)

    for row in range(cardsh):
        base = row * cardsw
        for col in range(cardsw):
            idx = base + col

            x = col * 8
            y = row * 8
            color = colorbands[row][col]
            bgi = color & 15
            bg = c64colors[bgi]
            fgi = (color >> 4) & 15
            fg = c64colors[fgi]

            draw = PIL.ImageDraw.Draw( colimg )
            draw.rectangle( (x,y,x+8,y+8), fill=bg)

            bwcard = colsource.crop( (x,y,x+8,y+8) )
            bwcard.load()
            card = bwcard.copy()
            draw.bitmap( (x,y), card, fill=fg)
    return colimg, bwimg
