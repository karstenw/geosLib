# geoPaint to PNG converter

A bunch of Python scripts to convert [GEOS](https://www.c64-wiki.de/index.php/GEOS) geoPaint images and Photo Album files in the CBM convert format to PNG.


Inspired by [geowrite2rtf](https://github.com/mist64/geowrite2rtf) by [Michael Steil](http://www.pagetable.com/). If you haven't seen his  [c64talk](https://www.youtube.com/watch?v=ZsRRCnque2E), go watch it.

I transfered the geowrite2rtf C program to Python. Having a quick success extracting the photoscrap data from a geoWrite doc I realized I really wanted a paint converter...

This started as weekend hack and the code still looks like it but for now it can convert most of the geoPaint files it encounters.

The geoPaint files must be in CBM CVT format to be converted.

The speed is now acceptable. It has been at 1.5s for 1 document. Now it converts 75 documents in under 15s.


# Update

+ The essential bug that made me output bw and color versions has been found: the entry for white in the color look up table was wrong. White was nearly black...

+ Photo Album V1 files are now converted too. Each entry is written as a file. Photo Album V2 files are not read. They crash and I can't find any documentation.

# Requisites
+ [pillow](https://github.com/python-pillow/Pillow)

# Usage:
```
python geoPaint2png.py testimages/*.cvt
```

# To do:

+ Finish the geoWrite converter. After all this is where it started.

+ Photo Album V2 files

+ Photo Scrap files

+ Text Album files

+ Text Scrap files

+ stop this trip on memory lane.
