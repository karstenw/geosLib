# geosLib

geosLib is a Python library to convert [GEOS](https://www.c64-wiki.de/index.php/GEOS) geoPaint, geoWrite, Photo Album and Photo Scrap files to modern formats.

Image files can be converted to PNG.

Text formats can be converted to RTFD, HTML ans TXT.

GEOS font files are rendered as PNG for each size.

# Requisites

+ [pillow](https://github.com/python-pillow/Pillow)

# Usage:
```

# for CBM Convert files in geoPaint, Photo Album, Photo Scrap, geoWrite, Text Album and Text Scrap format:
python convertCVTFiles.py *.cvt

```

# To do:

+ Text Album files

+ Some differences between "Write Image V2.0" and "Write Image V2.1"

+ geoPublish format? If someone has a pointer please write up an issue.


# Summary

+ Send CBM CVT files to CBMConvertFile and  DiskImages to DiskImage. Look at geosFiletypeScanner's usage of geosLib.getCompressedFile() on how to handle gzip and zip files.

+ IOW: get your geos file into a VLIRFile structure. The name is misleading since SEQ files go there too. That's what any of the conversion functions in geosLib expect.

# Update

+ Welcome the new addition macpaintLib.py. For the start it will be kept in it's own file but will be integrated after maturing. It uses a lot of common code and is very beta.
+ Currently it converts all but one from all the macpaint files I could find on the net.
  + sources so far;
    + [http://cd.textfiles.com/carousel344/PIC](http://cd.textfiles.com/carousel344/PIC)
    + [http://cd.textfiles.com/vgaspectrum/mac/mac1](http://cd.textfiles.com/vgaspectrum/mac/mac1)
    + [http://cd.textfiles.com/vgaspectrum/mac/mac2](http://cd.textfiles.com/vgaspectrum/mac/mac2)
  + If you find more macpaint files, please create an issue

+ Usage

```

python macpaintLib.py /Path/To/Folder/with/MacPaint/Files/

```

this will create a folder macpaintExports at the same location from where the script is started.