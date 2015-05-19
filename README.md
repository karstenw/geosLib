# geoPaint to PNG converter

A bunch of Python scripts to convert geoPaint images in the CBM convert format to PNG.


Inspired by [geowrite2rtf](https://github.com/mist64/geowrite2rtf) by [Michael Steil](http://www.pagetable.com/). If you haven't seen his  [c64talk](https://www.youtube.com/watch?v=ZsRRCnque2E), go watch it.

I transfered the geowrite2rtf C program to Python. Having a quick success extracting the photoscrap data from a geoWrite doc. Now I realized I really wanted a paint converter...

This started as weekend hack and the code still looks like it but for now it can convert most of the geoPaint files it encounters.

The geoPaint files must be in CBM CVT format to be converted.

# Requisites
+ [pillow](https://github.com/python-pillow/Pillow)

