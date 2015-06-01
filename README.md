# geosLib

geosLib is a Python library to convert [GEOS](https://www.c64-wiki.de/index.php/GEOS) geoPaint, geoWrite, Photo Album and Photo Scrap files to modern formats.

Image files can be converted to PNG.

Text formats can be converted to RTFD, HTML ans TXT.


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
