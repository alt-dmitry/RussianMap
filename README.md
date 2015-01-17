---
output:
  html_document:
    keep_md: yes
---
# RussianMap
##1. Polygons of russian administrative regions.

Final geojson files are:

- output.js. Here is all in one file.

- in subdataClean folder. Each file represents one region.

##2. Python script to implify coordinates

By changing c constant in the SimplifyCoordinates.py you can make a map a lot lighter.

Just make c smaller in order to build more simple polygons.

Apart from node coordinates geojson files have "Center_Opt" property with polygon centers and appropriate zoom level (for leaflet js).

##3. Example

You can take a look at it [here](http://alt-dmitry.github.io/RussianMap/map.html).

This example was created with [leafletjs](http://leafletjs.com).

##4. Copyright

I used data from [openstreetmaps](http://www.openstreetmap.org) and [gis-lab](http://gis-lab.info). It is free to use but do not forget to cite them!

