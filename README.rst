##############
FSim Readme
##############
Author: HanishKVC
Version: v20210929IST0052

Intro
########

A simple dumb flight sim with a futuristic all degree freedom space ship mode for now.
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

It allows height fields to be used as the terrain.

There is a helper script to which one can pass the USGS earth explorer GMTED2010 elevation data and inturn it will generate heightfield and colormap files which can be used by this program.
Pass the GeoTIFF file from USGS directly, dont use any image converter to create a png or jpg or so and then pass to this program, bcas it may lose some of the detail in the process.


