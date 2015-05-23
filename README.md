# geoPaint to PNG converter

A bunch of Python scripts to convert [GEOS](https://www.c64-wiki.de/index.php/GEOS) geoPaint images and Photo Album files in the CBM convert format to PNG.


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

# Requisites
+ [pillow](https://github.com/python-pillow/Pillow)

# Usage:
```

# for geoPaint, Photo Album & Photo Scrap files
python geoPaint2png.py *.cvt

# for a geoWrite file
python geowrite2rtf.py CVTFile

```

# To do:

+ Text Album files

+ Text Scrap files

+ Clean the mess up and finish this trip on memory lane.


# Some (cropped) old images:
![Woodblock](./images/Woodblock.png?raw=true)
![Lobster](./images/Lobster.png?raw=true)
![Shuttlelaunch](./images/Shuttlelaunch_col.png?raw=true)
![Zebragirl](./images/ZEBRAGIRL_bw.png?raw=true)
