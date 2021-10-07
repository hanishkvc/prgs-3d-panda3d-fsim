##############
FSim Readme
##############
Author: HanishKVC
Version: v20211007IST2026

Intro
########

One could either use it as a simple dumb flight sim with a futuristic all degree freedom space ship mode for now.
Or one could treat it as a simple heightfield 3D viewer.

Done to get some basic feel about Panda3D, and have some fun in the process.
Also bcas MS seems to have decided not to release MSFS on XBox1X (No No Noooo).


Usage
=======

Cmdline
----------

./fsim <options>

The supported options are

* --sTerrainFile <base_filename>

* --bTopView

  Show the terrain from above / top

* --help

  Will give all options supported in a given version of the program

* --bLODBruteForce

  The terrain will be generated with full level of detail throughtout. In this case the program will take more time to show the initial frame.
  And from then on the periodic terrain updates dont take any time to update, as full level detail for full terrain is already generated.

* --LODMinLevel <a int>

  0: Full level of detail for the terrain area within the near lod distance

  X: Any other integer value. As the integer value increases, lesser will be the maximum amount of detail that will be in generated terrain. So also terrain generate and update will take less time.


Keys
-------

SpaceShip mode

* Translation

  + w : move forward

  + s : move backward

  + a : move left (pan)

  + d : move right (pan)

  + q : move up (pan)

  + e : move down (pan)

* Rotation

  + i : rotate down

  + k : rotate up

  + j : rotate left

  + l : rotate right

  + u : tilt left

  + o : tilt right


Terrain
##########

It allows height fields to be used as the terrain. It uses the GeoMipTerrain module of Panda3D for this.

Two files are expected

   <terrainfilename>.hf.png - the heightfield image file corresponding to the terrain.
   <terrainfilename>.cm.png - the color map image file corresponding to the terrain.

Helper script is provided in utils folder to generate the above files from

   Elevation GeoTiff file
      for example the GMTED2010 elevation data from Nasa/USGS Earth Explorer

   Reference colormap file (optional, required if one wants a preexisting coloring for the terrain being worked on is to be used)
      for example if one is interested in having say the vegetation based coloring for the terrain, then one could pass the world vegetation GeoTiff file from Nasa/USGS/...


Helper script
==============

One passes the elevation data file and inturn it will generate the hf.png (heightfield) and cm.png (colormap) files, which can be used by this program.

NOTE: Pass the GeoTIFF file from USGS directly, dont use any image converter to create a png or jpg or so and then pass to this program, bcas it may lose some of the detail in the process.

The script resizes the passed image to be a power of 2 + 1 size image. During this process, it doesnt worry about the aspect ratio.

By default the colormap file generated is based on the relative height infered from the elevation image file (ie based on the intensity of the shade at corresponding pixel location).

It also allows one to generate a color map based on a reference image which also contains the co-ordinates belonging to the heightfield image being processed. For this both the heightfield/elevation file as well as the reference image need to be GeoTiff images, so that the helper script can try to map the heightfield file to its corresponding location in the reference image.


