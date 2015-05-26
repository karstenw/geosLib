# geoPaint to PNG converter

A bunch of Python scripts to convert [GEOS](https://www.c64-wiki.de/index.php/GEOS) geoPaint, geoWrite, Photo Album and Photo Scrap files in the CBM convert format to PNG for the images and to RTFD, TXT & HTML for the text formats.


Inspired by [geowrite2rtf](https://github.com/mist64/geowrite2rtf) by [Michael Steil](http://www.pagetable.com/). If you haven't seen his  [c64talk](https://www.youtube.com/watch?v=ZsRRCnque2E), go watch it.

I transfered the geowrite2rtf C program to Python. Having a quick success extracting the photoscrap data from a geoWrite doc I realized I really wanted a paint converter...

This started as weekend hack and the code still looks like it but for now it can convert most of the geoPaint files it encounters.

The geoPaint and Album files must be in CBM CVT format to be converted.

The speed is now acceptable. It has been at 1.5s for 1 document. Now it converts 75 documents in under 15s.


# Update


+ The essential bug that made me output bw and color versions has been found: the entry for white in the color look up table was wrong. White was nearly black...

+ Photo Album V1 files are now converted too. Each entry is written as a file.

+ The geowrite2rtf script now works too. Including images. Output is a OSX RTFD folder and a HTML folder.

+ Photo Album V2.1 works now. Scrap name gets copied into outfilename.

+ Now d64, d81 as well as their gzipped, zipped and zip collected variants can now be read. See geosFiletypeScanner.py tries to read anything you throw at it...


# Requisites
+ [pillow](https://github.com/python-pillow/Pillow)

# Usage:
```

# for CBM Convert files in geoPaint, Photo Album, Photo Scrap, geoWrite, Text Album and Text Scrap format:
python geoPaint2png.py *.cvt

```

# To do:

+ Text Album files

+ Some differences between "Write Image V2.0" and "Write Image V2.1"

+ Clean the mess up and finish this trip on memory lane.

# Summary

+ Send CBM CVT files to CBMConvertFile (in C64Data) DiskImages to DiskImage (also in c64Data). Look at geosFiletypeScanner's function getCompressedFile() on how to handle gzip and zip files.

+ IOW: get your geos file into a VLIRFile structure. The name is misleading since SEQ files go there too. That's what any of the conversion functions in geosData.py expect.