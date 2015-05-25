
# -*- coding: utf-8 -*-


import sys
import os
import datetime
import struct

import pprint
pp = pprint.pprint


import pdb
kwdbg = 0
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
    1, 2, 4, 5, 6, 9, 10, 14, 15)
programTypes = (
    1,2,4,5,6,9,10,11,12,14,15)
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

        v = VLIRFile()
        v.header = self.geosHeaderBlock
        v.dirEntry = self.geosDirEntry
        self.vlir = v
        geofiletype = ord(data[21])

        formatOK = False
        if format.startswith("PRG formatted GEOS file V1.0"):
            broken = False
            formatOK = True
        elif format.startswith("PRG formatted GEOS file"):
            broken = True
            formatOK = True
        elif format.startswith("SEQ formatted GEOS file"):
            # this is a new one
            broken = True
        else:
            print "ERROR: Unknown file format %s" % repr(format)
            formatOK = False
            broken = True

        if formatOK:
            if geofiletype == 0:
                # sequential file.
                # out of pure lazyness, store filadata in vlir[0]
                # why did I make the SEQFile class? Dismissed.
                v.chains[0] = data[0x1fc:]

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
                        v.chains[i] = (a1,a2)
                        break
        
                    if a1 == 0 and a2 == 255:
                        #v.chains[i] = (ai,a2)
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
        
                    v.chains[i] = chaindata

                    consumedpayload = chainend


class VLIRFile(object):
    def __init__(self):
        self.chains = [ (0x00, 0xff) ] * 127
        self.header = ""
        self.dirEntry = ""
        # for saving
        self.folder = ""
        self.filename = ""

def cleanupString( s ):
    # remove garbage
    t = s.strip( stripchars )
    return t.split( chr(0) )[0]
    

class GEOSHeaderBlock(object):

    def __init__(self, s, filepath):

        if kwdbg:
            self.rawdata = s
        # skip possible link bytes
        if ord(s[0]) == 0 and len(s) == 256:
            s = s[2:]
        # filepath is only needed for display purposes
        # have to think of sth for fileas from 
        self.filepath = filepath
        self.iconWidthCards = ord(s[0])
        self.iconWidth = self.iconWidthCards * 8
        self.iconHeight = ord(s[1])
        self.iconByteLength = ord(s[2]) & 0x7f
        self.iconDataRAW = s[3:3+63]

        # ok up to here
        self.dosFileTypeRAW = s[66]
        self.fileOK = (ord(self.dosFileTypeRAW) & 128) > 0
        self.fileProtected = (ord(self.dosFileTypeRAW) & 64) > 0
        t = ord(self.dosFileTypeRAW) & 7
        self.fileType = dosFileTypes.get(t, "???")

        # ok up to here
        self.geosFileType = ord(s[67])
        self.geosFileTypeString = geosFileTypes.get(self.geosFileType, "UNKNOWN GEOS filetype:%i" % self.geosFileType)

        # ok up to here
        self.geosFileStructure = ord(s[68])
        self.geosFileStructureString = ""
        if self.geosFileStructure == 0:
            self.geosFileStructureString = "Sequential"
        elif self.geosFileStructure == 1:
            self.geosFileStructureString = "VLIR"

        # ok up to here
        self.loadAddress = ord(s[69]) + ord(s[70]) * 256
        self.endOfLoadAddress = ord(s[71]) + ord(s[72]) * 256
        self.startAddress = ord(s[73]) + ord(s[74]) * 256

        # self.classNameRAW = s[75:95]
        self.className = cleanupString(s[75:91])
        
        self.fourtyEighty = fourtyEighty.get(ord(s[94]), "")
        
        authorOrParentDisk = cleanupString( s[95:115] )
        self.author = self.parentDisk = ""
        if self.geosFileType in filetypesWithAuthor:
            self.author = authorOrParentDisk
        else:
            self.parentDisk = authorOrParentDisk

        self.creator = cleanupString( s[115:135] )
        
        self.applicationData = s[135:157]

        # geoWrite specific header data
        self.firstPagenumber = 1
        self.NLQPrint = self.titlePage = False
        self.headerHeight = self.footerHeight = self.pageHeight = 0
        if self.className.startswith( "Write Image V" ):
            self.firstPagenumber = ord(s[0x87]) + ord(s[0x88]) * 256
            
            self.NLQPrint = (ord(s[0x89]) & 64) > 0
            self.titlePage = (ord(s[0x89]) & 128) > 0
            self.headerHeight = ord(s[0x8a]) + ord(s[0x8b]) * 256
            self.footerHeight = ord(s[0x8c]) + ord(s[0x8d]) * 256
            self.pageHeight = ord(s[0x8e]) + ord(s[0x8f]) * 256
        self.desktopNote = cleanupString(s[158:])

    def prnt(self):
        print
        print "GEOS Header Block for:", repr(self.filepath)
        
        # print icon
        print '-' * 24
        for y in range(21): # self.iconHeight):
            for x in range(3): # self.iconWidthCards):
                # i = ord(self.iconDataRAW[y*self.iconWidthCards+x])
                i = ord(self.iconDataRAW[y*3+x])
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

        print "GEOS Class Name:", repr(self.className)
        if self.geosFileType in filetypesWithAuthor:
            print "GEOS Author Name:", repr(self.author)
        else:
            print "GEOS Parent Disk:", repr(self.parentDisk)
        print "GEOS Creator Name:", repr(self.creator)
        print "GEOS 40/80:", self.fourtyEighty
        print "GEOS Load Address:", hex(self.loadAddress)
        print "GEOS End Address:", hex(self.endOfLoadAddress)
        print "GEOS Exe Address:", hex(self.startAddress)
        if self.className.startswith( "Write Image V" ):
            print "geoWrite first page number:", self.firstPagenumber
            print "geoWrite NLQ print:", self.NLQPrint
            print "geoWrite first page is Title:", self.titlePage
            print "geoWrite header height:", self.headerHeight
            print "geoWrite footer height:", self.footerHeight
            print "geoWrite page height:", self.pageHeight
        print "GEOS DeskTop Comment:", repr(self.desktopNote)


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


class GEOSDirEntry(object):
    def __init__(self, s, isGeos=True):
    
        if len(s) == 32:
            s = s[2:]
        
        self.dosFileTypeRAW = s[0]
        self.fileOK = (ord(self.dosFileTypeRAW) & 128) > 0
        self.fileProtected = (ord(self.dosFileTypeRAW) & 64) > 0
        t = ord(self.dosFileTypeRAW) & 7

        self.fileType = dosFileTypes.get(t, "???")
        self.trackSector = (ord(s[1]), ord(s[2]))
        self.fileName = s[0x03:0x13]
        self.fileName = self.fileName.rstrip(stripchars)
        
        self.geosHeaderTrackSector = (0,0)
        self.fileSizeBlocks = ord(s[0x1c]) + ord(s[0x1d]) * 256

        # if not geos, this is REL side sector
        self.geosHeaderTrackSector = (ord(s[19]), ord(s[20]))
        # if not geos, this is REL record size
        self.geosFileStructure = ord(s[21])
        self.geosFileStructureString = ""
        self.geosFileTypeString = ""
        self.modfDate = "NO MODF DATE"
        self.isGEOSFile = False

        if self.fileType == 'USR':
            if self.geosFileStructure == 0:
                self.geosFileStructureString = "Sequential"
                self.isGEOSFile = True
            elif self.geosFileStructure == 1:
                self.geosFileStructureString = "VLIR"
                self.isGEOSFile = True

            self.geosFileType = ord(s[22])
            #self.geosFileTypeString = geosFileTypes[self.geosFileType]
            self.geosFileTypeString = geosFileTypes.get(self.geosFileType, "UNKNOWN GEOS filetype:%i" % self.geosFileType)

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

    def prnt(self):
        print 
        print '-' * 80
        print "filename:", repr(self.fileName)
        print '-' * 16
        print "file OK:", self.fileOK
        print "file Protected:", self.fileProtected
        print "file type:", self.fileType
        print "file Track/Sector:", self.trackSector
        print "GEOS Header Track/Sector:", self.geosHeaderTrackSector
        print "GEOS File Structure:", self.geosFileStructureString
        print "GEOS File Type:", self.geosFileTypeString
        print "GEOS File Last Modified:", str(self.modfDate)[:19]
        print "GEOS Total Block Size:", self.fileSizeBlocks
        print 
    def smallprnt(self):
        print repr(self.fileName).ljust(20), str(self.fileSizeBlocks).rjust(5), repr(self.fileType)

class ImageBuffer(list):
    def __init__(self):
        super(ImageBuffer, self).__init__()
    def dump(self):
        hexdump( self )
        
def hexdump( s, col=32 ):
    cols = {
         8: ( 7, 0xfffffff8),
        16: (15, 0xfffffff0),
        32: (31, 0xffffffe0),
        64: (63, 0xffffffc0),
    }
    if not col in cols:
        col = 16
    minorMask, majorMask = cols.get(col)
    d = False
    mask = col-1
    if type(s) in( list, tuple): #ImageBuffer):
        d = True
    for i,c in enumerate(s):
        if d:
            t = hex(c)[2:]
        else:
            t = hex(ord(c))[2:]
        t = t.rjust(2, '0')
        
        if i % col == 0:
            a = hex(i)[2:]
            a = a.rjust(4,'0')
            sys.stdout.write(a+':  ')
        sys.stdout.write(t+' ')
        if i & minorMask == minorMask:
            offs = i & majorMask
            
            for j in range(col):
                c2 = s[offs+j]
                d2 = ord(c2)
                if 32 <= d2 < 127:
                    sys.stdout.write( c2 )
                else:
                    sys.stdout.write( '.' )
            sys.stdout.write('\n')

# drive geometries
sectorTables = {
    '.d64': (
            ( 0,  0,  0),
            ( 1, 17, 21),
            (18, 24, 19),
            (25, 30, 18),
            (31, 35, 17)),

    '.d71': (
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
            (66, 70, 17)),

    '.d81': (
            ( 0,  0,  0),
            # side 1
            ( 1, 40, 40),
            # side 2
            (41, 80, 40))
}

minMaxTrack = {
    '.d81': (1,80),
    '.d64': (1,35),
}

extToImagesize = {
    # ext, filesize, sector count
    '.d64': ((174848,  683),),
    '.d81': ((819200, 3200),),
    '.d71': ((349696, 1366),
             (349696+1366, 1366)) }

imagesizeToExt = {
    # filesize, ext, sector count
    174848: ( '.d64',  683),
    175531: ( '.d64',  683),
    819200: ('.d81', 3200),
    349696: ('.d71', 1366),
    351062: ('.d71', 1366)}

dirSectorsForDrives = {
    '.d64': (18, 0),
    '.d81': (40, 0)}

dirSectorStructures = {
    '.d64': ("<b b  c      c    140s 16s 2x 2s x   2s 4x b     b     11s       5s 67x", 
             "tr sc format dosv1 bam dnam   diskid dosv2 dsktr dsksc geoformat geoversion"),
    '.d81': ("<b b  cx  16s 2x 2s x 2s 2x 3x 96s 16x 16s 2x 9x b b 11s 5s 3x 64x",
             "tr sc fmt dnam   dskid dosv power64 geoname dsktr dsksc geoformat geoversion")}
    #'.d81org': ("< x x x x 16s 2x 2s x 2x 2x 227x",
    #         "tr sc fmt d1 dnam d2 dskid d3 dosv d4 d5")}



class DiskImage(object):

    def getTrackOffsetList(self, sizelist ):
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

    def readfile( self, path):
        f = open(path, 'rb')
        s = f.read()
        f.close()
        return s

    def getTS(self, t, s):
        error = ""
        if t == 0:
            return "", ""
        try:
            # size = 256
            if self.minMaxTrack[0] <= t <= self.minMaxTrack[1]:
                if 0 <= s <= self.sectorsPerTrack[t]:
                    adr = self.trackByteOffsets[t-1] + s * 256
                    data = self.stream[adr:adr+256]
                else:
                    return "",""
            else:
                return "",""
            
        except Exception, err:
            print "getTS(%i,%i) ERROR: %s" % (t,s,err)
            return err, ""
            # pdb.set_trace()
            print 
            #print "adr", adr
            #print "adr+256", adr+256
            #print len(self.stream)
            # error = err
        return error, data
    
    def getChain(self, t, s):
        error = ""
        readSoFar = set()
        # pdb.set_trace()
        result = []
        tr, sc = t, s
        blocks = 0
        while True:
            blocks += 1
            err, b = self.getTS(tr, sc)
            readSoFar.add( (tr,sc) )
            if err != "":
                s = ''.join( result )
                return err, s
            if len(b) <= 2:
                # pdb.set_trace()
                break
            tr = ord(b[0])
            sc = ord(b[1])
            if tr == 0:
                result.append( b[2:sc+1] )
                break
            elif (tr,sc) in readSoFar:
                # circular link
                # pdb.set_trace()
                if len(b) > 2:
                    result.append( b[2:] )
                break
            elif tr > 80:
                break
            else:
                result.append( b[2:] )
        return error, ''.join( result )

    def getDirEntries(self, t, s):
        """Read all file entries"""
        readSoFar = set()
        error = ""
        result = []
        if t == 0:
            return "", result
        nextrack, nextsector = t, s
        while True:
            readSoFar.add( (nextrack, nextsector) )
            err, b = self.getTS( nextrack, nextsector)
            if err != "":
                break
                # return err, result
            if not b:
                break
            
            nextrack, nextsector = ord(b[0]), ord(b[1])
            if (nextrack, nextsector) in readSoFar:
                break
            base = 0
            for i in range(8):
                offset = i * 32
                dirEntryRaw = b[offset:offset+32]
                gde = GEOSDirEntry(dirEntryRaw)
                if gde.fileType in ( 'SEQ', 'PRG', 'USR'):
                    result.append( gde )
        return error, result
    
    def printDirectory(self):
        # print directory
        print
        print '#' * 40
        print repr(self.diskName)
        print '-' * 20
        for i in self.DirEntries:
            i.smallprnt()
        if self.deskBorder:
            print
            print "On Desktop border:"
        for i in self.deskBorder:
            i.smallprnt()
        print

    def __init__(self, stream=None, filepath=None, tag=""):
        # pdb.set_trace()
        # alternate path for streams
        self.tag = tag
        self.filepath = ""
        self.stream = ""
        if filepath:
            if os.path.exists( filepath ):
                self.filepath = os.path.abspath(os.path.expanduser(filepath))
                self.stream = self.readfile( self.filepath )
            else:
                print "No File ERROR!"
                pdb.set_trace()
        elif stream:
            self.stream = stream
        else:
            pdb.set_trace()
            print
        self.isOK = False
        self.files = []
        size = len(self.stream)
        typ, sectorcount = imagesizeToExt.get( size, ("",0) )
        
        if typ in ('.d64', '.d81'): # '.d71'):

            self.isOK = True

            o,p,t = self.getTrackOffsetList( sectorTables[typ] )
            self.sectorOffsets, self.trackByteOffsets, self.sectorsPerTrack = o,p,t
            self.dirSectorTS = dirSectorsForDrives.get(typ, (0,0))

            self.minMaxTrack = minMaxTrack[typ]

            dtr, dsc = self.dirSectorTS
        
            s,n = dirSectorStructures[typ]
            err, dirSec = self.getTS( dtr, dsc )
            if err != "":
                pdb.set_trace()
            t = struct.unpack(s, dirSec)
            n = n.split()
            d = dict(zip(n,t))
            s = d.get('dnam', 'NO DISK NAME')
            s = s.rstrip( chr(int("a0",16)))
            self.diskName = s
        
            self.isGEOSDisk = d['geoformat'] == "GEOS format"
        
            err, self.DirEntries = self.getDirEntries( d['tr'], d['sc'])
            
            self.deskBorder = []
            if self.isGEOSDisk:
                err, self.deskBorder = self.getDirEntries( d['dsktr'], d['dsksc'])

            # get files
            dirEntries = self.DirEntries[:]
            if self.isGEOSDisk and self.deskBorder:
                # pdb.set_trace()
                dirEntries.extend( self.deskBorder )

            for dirEntry in dirEntries:
                # 
                # dirEntry.smallprnt()
                f = VLIRFile()
                f.dirEntry = dirEntry
            
                isGEOSFile = dirEntry.isGEOSFile
                isVLIR = dirEntry.geosFileStructureString == 'VLIR'

                f.header = ""
                if isGEOSFile:
                    err, s = self.getTS( dirEntry.geosHeaderTrackSector[0],
                                    dirEntry.geosHeaderTrackSector[1] )
                    if len(s) == 256:
                        src = "IMAGE:" + repr(dirEntry.fileName)
                        if self.filepath:
                            src = self.filepath
                        f.header = GEOSHeaderBlock(s, src)

                # file content
                t,s = dirEntry.trackSector
                if isGEOSFile:
                    if isVLIR:
                        # ATTN: due to the prior implementation of CBM-CVT files
                        # VLIR header (VLIRFile.__init__)is missing the link bytes
                        err, vlirhead = self.getTS( t, s)
                        if err:
                            print "NO VLIR"
                            pdb.set_trace()
                            print
                        if not vlirhead:
                            continue
                        # pdb.set_trace()
                        for i in range(127):
                            t = ord(vlirhead[i*2+0])
                            s = ord(vlirhead[i*2+1])
                            # print i*2,t,s
                            if t != 0:
                                err, f.chains[i] = self.getChain(t, s)
                            else:
                                f.chains[i] = (t,s)
                    else:
                        err, f.chains[0] = self.getChain(t, s)
                else:
                    err, f.chains[0] = self.getChain(t, s)

                self.files.append( f )
            if kwdbg:
                self.printDirectory()


if __name__ == '__main__':
    if 0:
        # make an image with the c64 colors
        import PIL
        import PIL.Image
        import PIL.ImageDraw
    
        c = 512
        d = c >> 2
        c64colrect = PIL.Image.new('RGB', (c,c), (1,1,1))
        draw = PIL.ImageDraw.Draw( c64colrect )
        for y in range(4):
            for x in range(4):
                col = y * 4 + x
                xc = x * d
                yc = y * d
                col = c64colors[col]
                draw.rectangle((xc,yc,xc+d,yc+d), fill=col, outline=None)
            
        c64colrect.save("C64 colors.png")
    
    if 1:
        pdb.set_trace()
        for f in sys.argv[1:]:
            e = DiskImage( filepath=f )
        pdb.set_trace()
        print
