
# -*- coding: utf-8 -*-


import sys
import os
import datetime

import pdb
kwlog = 0

# unused and incomplete (yet)
fontmapping = {
    0: ('BSW', ''),
    1: ('University', ''),
    2: ('California', ''),
    3: ('Roma', 'Times'),
    4: ('Dwinelle', ''),
    5: ('Cory', ''),
    6: ('Tolman', ''),
    7: ('Bubble', ''),
    8: ('Fontknox', ''),
    9: ('Harmon', 'Courier'),
    10: ('Mykonos', ''),
    11: ('Boalt', ''),
    12: ('Stadium', ''),
    14: ('Evans', ''),
    13: ('Tilden', ''),
    15: ('Durant', ''),
    16: ('Telegraph', ''),
    17: ('Superb', ''),
    18: ('Bowditch', 'Palatino'),
    19: ('Ormond', ''),
    20: ('Elmwood', ''),
    21: ('Hearst', ''),
    21: ('Brennens (BUG)', ''),
    23: ('Channing', ''),
    24: ('Putnam', ''),
    25: ('LeConte', '')}

c64colors = {
    0: (0,0,0),
    1: (255,255,255),
    2: (0x88,0,0),
    3: (0xaa,0xff,0xee),

    4: (0xcc,0x44,0xcc),
    5: (0x00,0xcc,0x55),
    6: (0x00,0x00,0xaa),
    7: (0xee,0xee,0x77),
    8: (0xdd,0x88,0x55),
    9: (0x66,0x44,0x00),
    10: (0xff,0x77,0x77),
    11: (0x33,0x33,0x33),
    12: (0x77,0x77,0x77),
    13: (0xaa,0xff,0x66),
    14: (0x00,0x88,0xff),
    15: (0xbb,0xbb,0xbb)}

geosFileTypes = {
    0: 'Non-GEOS file',
    1: 'BASIC Program',
    2: 'Assembly program',
    3: 'Data file',
    4: 'System file',
    5: 'Desk Accessory',
    6: 'Application',
    7: 'Application Data',
    8: 'Font file',
    9: 'Printer driver',
    10: 'Input driver',
    11: 'Disk Device',
    12: 'System Boot file',
    13: 'Temporary',
    14: 'Auto Executing',
    15: 'Input 128'}

filetypesWithAuthor = (
    1, 2, 5, 6, 9, 10, 15)

dosFileTypes = {
    0: 'DEL',
    1: 'SEQ',
    2: 'PRG',
    3: 'USR',
    4: 'REL',
    5: 'CBM'}

fourtyEighty = {
    0:    "GEOS 64/128 40 columns",
    64:   "GEOS 64/128 40/80 columns",
    128:  "GEOS 64 40 columns",
    192:  "GEOS 128 80 columns"}

stripchars = ''.join( (chr(0),chr(0xa0)) )


class CBMConvertFile(object):
    def __init__(self, filepath):

        infile = filepath
        infile = os.path.abspath(os.path.expanduser(infile))

        self.folder, filename = os.path.split( infile )
        basename, ext = os.path.splitext( filename )

        f = open(infile, 'rb')
        data = f.read()
        f.close()

        self.direntry = data[0:0x1e]

        self.geosDirEntry = GEOSDirEntry(self.direntry)

        format = data[0x1e:0x3a]

        geoinfo = data[0xfe:0x1fc]
        self.geosHeaderBlock = GEOSHeaderBlock(geoinfo, infile)

        giwidth = ord( geoinfo[0] ) * 8
        giheight = ord( geoinfo[1] )
        gibitmapType = ord( geoinfo[2] )
        gispritedata = geoinfo[3:66]
    
        gidosfiletype = ord( geoinfo[66] )
        gigeosfiletype = ord( geoinfo[67] )
        gigeosfilestructure = ord( geoinfo[68] )
    
        if 0: #kwlog:
            print "icon width:", giwidth
            print "icon height:", giheight
            print "bitmap type", gibitmapType
            print "DOS file type:", gidosfiletype
            print "GEOS file type:", gigeosfiletype
            print "GEOS file structure:", gigeosfilestructure

        if format.startswith("PRG formatted GEOS file V1.0"):
            broken = False
        elif format.startswith("PRG formatted GEOS file"):
            broken = True
        else:
            print "ERROR: Unknown file format %s" % repr(format)
            return None

        if 0: #kwlog:
            print "<<<%s>>>" % format

        geofiletype = ord(data[21])

        chains = [ (0x00, 0xff) ] * 127

        if geofiletype == 0:
            # sequential file.
            # out of pure lazyness, store filadata in vlir[0]
            # why did I make the SEQFile class?
            chains[0] = data[0x1fc:]

        elif geofiletype == 1:
            vlirheader = data[0x1fc:0x2fa]

            payload = data[0x2FA:]

            consumedpayload = 0

            for i in range( 127 ):
                a1 = ord( vlirheader[i * 2] )
                a2 = ord( vlirheader[i * 2 + 1] )
                if 0: #kwlog:
                    print "<<<chain 0x%02x/0x%02x>>>" % ( a1, a2 )
        
                # end of file
                if a1 == 0 and a2 == 0:
                    chains[i] = (a1,a2)
                    break
        
                if a1 == 0 and a2 == 255:
                    #chains[i] = (ai,a2)
                    continue
        
                if broken:
                    chain_size = a1 * 254 + a2
                    gross_size = chain_size
                else:
                    chain_size = (a1 - 1) * 254 + a2 -1
                    gross_size = a1 * 254

                chainstart = consumedpayload
                chainend = consumedpayload + gross_size
                chainlogicalend = consumedpayload + chain_size
                chaindata = payload[chainstart:chainlogicalend]
        
                chains[i] = chaindata

                consumedpayload = chainend
        v = VLIRFile()
        v.chains = chains
        v.header = self.geosHeaderBlock
        v.dirEntry = self.geosDirEntry
        self.vlir = v


class VLIRFile(object):
    def __init__(self):
        self.chains = None
        self.header = None
        self.dirEntry = None


class SEQFile(object):
    def __init__(self):
        self.data = None
        self.header = None
        self.dirEntry = None


class GEOSHeaderBlock(object):
    def __init__(self, s, filepath):
        # skip possible link bytes
        if ord(s[0]) == 0 and len(s) == 256:
            s = s[2:]
        # pdb.set_trace()
        self.filepath = filepath
        self.iconWidthCards = ord(s[0])
        self.iconWidth = self.iconWidthCards * 8
        self.iconHeight = ord(s[1])
        self.iconByteLength = ord(s[2]) & 0x7f
        self.iconDataRAW = s[3:3+63]


        self.dosFileTypeRAW = s[66]
        self.fileOK = (ord(self.dosFileTypeRAW) & 128) > 0
        self.fileProtected = (ord(self.dosFileTypeRAW) & 64) > 0
        t = ord(self.dosFileTypeRAW) & 7
        self.fileType = dosFileTypes[t]

        self.geosFileType = ord(s[67])
        self.geosFileTypeString = geosFileTypes[self.geosFileType]

        self.geosFileStructure = ord(s[68])
        if self.geosFileStructure == 0:
            self.geosFileStructureString = "Sequential"
        elif self.geosFileStructure == 1:
            self.geosFileStructureString = "VLIR"

        self.loadAddress = ord(s[69]) + ord(s[70]) * 256
        self.endOfLoadAddress = ord(s[71]) + ord(s[72]) * 256
        self.startAddress = ord(s[73]) + ord(s[74]) * 256


        self.classNameRAW = s[0x4b:0x5e]
        # possible error here: geoPaint has leading 0x00; offset seems right
        self.classNameString = self.classNameRAW.strip( stripchars )
        
        self.fourtyEighty = ord(s[94])
        self.fourtyEightyString = fourtyEighty[self.fourtyEighty]
        
        self.authorRAW = s[94:94+20]
        self.authorString = self.authorRAW.split( chr(0) )[0]
        
        self.creatorRAW = s[114:114+20]
        self.creatorString = self.creatorRAW.rstrip( chr(0) )
        
        self.applicationData = s[134:0x9e]

        if self.classNameString.startswith( "Write Image V" ):
            self.firstPagenumber = ord(s[0x87]) + ord(s[0x88]) * 256
            
            self.NLQPrint = (ord(s[0x89]) & 64) > 0
            self.titlePage = (ord(s[0x89]) & 128) > 0
            self.headerHeight = ord(s[0x8a]) + ord(s[0x8b]) * 256
            self.footerHeight = ord(s[0x8c]) + ord(s[0x8d]) * 256
            self.pageHeight = ord(s[0x8e]) + ord(s[0x8f]) * 256


        self.desktopNoteRAW = s[0xa0-2:]
        self.desktopNoteString = self.desktopNoteRAW.split( chr(0) )[0]

    def prnt(self):
        print
        print "GEOS Header Block for:", repr(self.filepath)
        
        # print icon
        print '-' * 24
        for y in range(self.iconHeight):
            for x in range(self.iconWidthCards):
                i = ord(self.iconDataRAW[y*self.iconWidthCards+x])
                s = str(bin(i))
                s = s[2:]
                s = s.rjust(8,'0')
                s = s.replace('1', 'X')
                s = s.replace('0', ' ')
                sys.stdout.write(s)
                if x == 2:
                    sys.stdout.write('|')
            sys.stdout.write('\n')
        sys.stdout.flush()
        print '-' * 24
        
        # print extended file attributes
        print "GEOS File Structure:", self.geosFileStructureString
        print "GEOS File Type:", repr(self.geosFileTypeString)

        print "GEOS Class Name:", repr(self.classNameString)
        print "GEOS Author Name:", repr(self.authorString)
        print "GEOS Creator Name:", repr(self.creatorString)
        print "GEOS 40/80:", self.fourtyEightyString
        print "GEOS Load Address:", hex(self.loadAddress)
        print "GEOS End Address:", hex(self.endOfLoadAddress)
        print "GEOS Exe Address:", hex(self.startAddress)
        if self.classNameString.startswith( "Write Image V" ):
            print "geoWrite first page number:", self.firstPagenumber
            print "geoWrite NLQ print:", self.NLQPrint
            print "geoWrite first page is Title:", self.titlePage
            print "geoWrite header height:", self.headerHeight
            print "geoWrite footer height:", self.footerHeight
            print "geoWrite page height:", self.pageHeight
        print "GEOS DeskTop Comment:", repr(self.desktopNoteString)


class CBMDirEntry(object):
    pass


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


class GEOSDirEntry(CBMDirEntry):
    def __init__(self, s):
        self.dosFileTypeRAW = s[0]
        self.fileOK = (ord(self.dosFileTypeRAW) & 128) > 0
        self.fileProtected = (ord(self.dosFileTypeRAW) & 64) > 0
        t = ord(self.dosFileTypeRAW) & 7
        self.fileType = dosFileTypes[t]

        self.trackSector = (ord(s[1]), ord(s[2]))
        self.fileName = s[0x03:0x13]
        self.fileName = self.fileName.rstrip(stripchars)
        
        self.geosHeaderTrackSector = (ord(s[19]), ord(s[20]))

        self.geosFileStructure = ord(s[21])
        if self.geosFileStructure == 0:
            self.geosFileStructureString = "Sequential"
        elif self.geosFileStructure == 1:
            self.geosFileStructureString = "VLIR"

        self.geosFileType = ord(s[22])
        self.geosFileTypeString = geosFileTypes[self.geosFileType]

        self.modfDateRAW = s[0x17:0x1c]
        dates = [ord(i) for i in self.modfDateRAW]
        y,m,d,h,mi = dates

        if 85 <= y <= 99:
            y += 1900
        else:
            y += 2000
        try:
            self.modfDate = datetime.datetime(y,m,d,h,mi)
        except Exception, err:
            self.modfDate = "ERROR WITH:  %i %i %i - %i:%i" % (y,m,d,h,mi)
        
        self.fileSizeBlocks = ord(s[0x1c]) + ord(s[0x1d]) * 256

    def prnt(self):
        print "file OK:", self.fileOK
        print "file Protected:", self.fileProtected
        print "file type:", self.fileType
        print "file Track/Sector:", self.trackSector
        print "filename:", repr(self.fileName)
        print "GEOS Header Track/Sector:", self.geosHeaderTrackSector
        print "GEOS File Structure:", self.geosFileStructureString
        print "GEOS File Type:", self.geosFileTypeString
        print "GEOS File Last Modified:", str(self.modfDate)[:19]
        print "GEOS Total Block Size:", self.fileSizeBlocks

class ImageBuffer(list):
    def __init__(self):
        super(ImageBuffer, self).__init__()
    def dump(self):
        hexdump( self )
        
def hexdump( s ):
    d = False
    if type(s) in( list, ImageBuffer):
        d = True
    for i,c in enumerate(s):
        if d:
            t = hex(c)[2:]
        else:
            t = hex(ord(c))[2:]
        t = t.rjust(2, '0')
        
        if i % 16 == 0:
            a = hex(i)[2:]
            a = a.rjust(4,'0')
            sys.stdout.write(a+':  ')
        sys.stdout.write(t+' ')
        if i & 15 == 15:
            sys.stdout.write('\n')


# drive geometries
d1541Sectors = (
    ( 0,  0,  0),
    ( 1, 17, 21),
    (18, 24, 19),
    (25, 30, 18),
    (31, 35, 17) )

d1571Sectors = (
    ( 0,  0,  0),
    # side 1
    ( 1, 17, 21),
    (18, 24, 19),
    (25, 30, 18),
    (31, 35, 17),
    # side 2
    (36, 52, 21),
    (53, 59, 19),
    (60, 65, 18),
    (66, 70, 17))

d1581Sectors = (
    ( 0,  0,  0),
    # side 1
    ( 1, 40, 40),
    # side 2
    (41, 80, 40) )

imagesizes = {
    # ext, filesize, sector count

    '.d64': ((174848,  683),),

    '.d81': ((819200, 3200),),

    '.d71': ((349696, 1366),
             (349696+1366, 1366))

}
    

def getTrackOffsetList( sizelist ):
    """calculate sectorOffset per Track, track Byte offstes and
       sectors per track lists."""

    offset = 0
    sectorsize=256
    sectorOffsets = []
    trackByteOffsets = []
    sectorsPerTrack = []
    for start, end, sectors in sizelist:
        for track in range(start, end+1):
            offset += sectors 
            sectorOffsets.append(offset)
            sectorsPerTrack.append( sectors )
    for start, end, sectors in sizelist:
        for track in range(start, end+1):
            if track == 0:
                continue
            trackByteOffsets.append( (sectorOffsets[track-1]) * sectorsize )
    return sectorOffsets, trackByteOffsets, sectorsPerTrack






class DiskImage(object):


    d1541HeaderTS = (18, 0)
    d1581HeaderTS = (40, 0)

    d1541HdrStruct = "< xx x x 140x 16s xx 2s x xx xxxx 85x"
    d1541Names = ("next format dum1 bam nameraw dum2 diskid "
                  "dum3 dosversion dum4 dum5").split()

    d1581HdrStruct = "< xx x x 16s xx 2s x xx xx 227x"
    d1581Names = ("next format dum1 nameraw dum2 diskid "
                  "dum3 dosversion dum4 dum5").split()

    def __init__(self, stream=None, filepath=None):
        pass



if __name__ == '__main__':
    import PIL
    import PIL.Image
    import PIL.ImageDraw
    
    c64colrect = PIL.Image.new('RGB', (128,128), (1,1,1))
    draw = PIL.ImageDraw.Draw( c64colrect )
    for y in range(4):
        for x in range(4):
            col = y * 4 + x
            print col
            xc = x * 32
            yc = y * 32
            col = c64colors[col]
            draw.rectangle((xc,yc,xc+32,yc+32), fill=col, outline=None)
            
    c64colrect.save("C64 colors.png")