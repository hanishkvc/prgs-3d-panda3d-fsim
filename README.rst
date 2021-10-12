##############
FSim Readme
##############
Author: HanishKVC
Version: v20211012IST2006

Intro
########

One could either use it as a

a) simple heightfield 3D viewer with 6 degrees of freedom wrt movement

OR

b) simple less than minimal flight sim with either a

   1) futuristic antigrav engine ;) based spaceship kind of control mode (ie the 6 degrees of movement freedom) OR

   2) a very very crude hybrid of a powered glider/aircraft with few strange capabilities ;)

This was done to get some basic feel about Panda3D, and have some fun in the process.
Also bcas MS seems to have decided not to release MSFS on XBox1X (No No Noooo).

This provides a 1st person (from imagniary cockpit) view.

Usage
=======

Intro
-------

This involves

* first creating the terrain and related files

followed by

* flying around those terrain files.


One liners
--------------

One time airports(airfields/etal) objects db creation [Optional]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

utils/hkvc-aptdat.py data/apt.dat

This creates a odb.pickle file under data.

The apt.dat is the airports data file from X-Plane/Flightgear (one can get this from flightgears fgdata repo).

Additionally for each region/terrain, one needs to create the corresponding objects file,
which will help place the airports into the 3D scenery.

NOTE: Airports/etal appear as simple floating boxes (with their ICAO code on one side) above the ground, for now.


Creating the terrain and related file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create <terrain>.hf.png and <terrain>.cm.png files

utils/hkvc_imgutils.py --sCmd p3dterrain --sFNameSrc data/10n060e_20101117_gmted_mea300.tif

Optionally create the <terrain>.objects file

utils/hkvc_imgutils.py --sCmd mapobjects --sFNameSrc data/10n060e_20101117_gmted_mea300.tif --sFNameODB data/odb.pickle


Flying
~~~~~~~~

As a 3D Full resolution Terrain heightfield viewer

./fsim.py --sTerrainFile data/10n060e_20101117_gmted_mea300.tif --bLODBruteForce True

NOTE: Depending on ones machine, this could take some time to show the 3d terrain as well as maybe jerky while moving around.

As a 3D low resolution Terrain heightfield viewer

./fsim.py --sTerrainFile data/10n060e_20101117_gmted_mea300.tif --iLODMinLevel 2

As a simple dumb flightsim flying a advanced spaceship with full freedom of movement.

./fsim.py --sTerrainFile data/10n060e_20101117_gmted_mea300.tif --iLODMinLevel 2

As a simple dumb flightsim flying a flawed aircraft with limited freedom of movement.

./fsim.py --sTerrainFile data/10n060e_20101117_gmted_mea300.tif --iLODMinLevel 2 --bModeAC True



The Viewer/FlightSim
######################


cmdline args
==============

./fsim <options>

The supported options are

* --sTerrainFile <base_filename>

* --bTopView

   Show the terrain from above / top

   Default: False

* --help

   Will give options supported in a given version of the program

* --bLODBruteForce

   The full terrain will be generated with full level of detail in 3D.

   In this case the program may take more/some time to show the initial frame (depends on ones machine). And from then on
   the periodic terrain updates dont take any time to update, as full level detail for full terrain is already generated.

   Default: False

* --iLODMinLevel <int>

   0: Full level of detail for the terrain area within the near lod distance

   X: Any other integer value. As the integer value increases, lesser will be the maximum amount of detail that will be in generated terrain. So also terrain generate and update will take less time.

   On a machine with powerfull processor and graphics card use 0, in others use what is feasible.

* --bModeAC <True|False>

   True: run in a crude powered glider/aircraft mode

   False: run with 6 degree of freedom (advanced antigrav engine mode ;)

   Default: False


NOTE: By default (ie --bLODBruteForce false) the program will try to show a relatively higher resolution terrain only around the user/camera area
and low resolution terrain farther out. Inturn as one moves further out the program will periodically trigger regeneration of the terrain with
better resolution around the new position. This may occur almost immidiately or take time, based on ones machine.


Modes and Keys
================

SpaceShip mode
----------------

This provides a full freedom of movement wrt translation along all 3 axis as well as 3 degrees of freedom wrt rotation.

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


In this mode the logic will allow one to go below the terrain.


Aircraft mode
---------------

IN this mode, one can control the speed as well as the pitch and tilt.

In very curde ways based on speed lift will be generated, equally altitude and angle/pitch will affect the lift to some extent.

   + i : speed up

   + k : slow down

   + w : pitch down

   + s : pitch up

   + a : turn left

   + d : turn right

   + q : tilt left

   + e : tilt right

In this mode, the logic will try to force the aircraft to remain above the ground/terrain level.


Terrain
##########

It allows height fields to be used as the terrain. It uses the GeoMipTerrain module of Panda3D for this.

Two files are expected

   <terrainfilename>.hf.png - the heightfield image file corresponding to the terrain.

   <terrainfilename>.cm.png - the color map image file corresponding to the terrain.

Helper script is provided in utils folder to generate these files.

Helper script
==============

General
----------

One passes the elevation data file and inturn it will generate the hf.png (heightfield) and cm.png (colormap/texture) files, which can be used by the fsim program.

The script resizes the passed image to be a power of 2 + 1 size image. During this process, it doesnt worry about the aspect ratio.

Helper script expects the following file types to be provided to generate the above files

* Elevation GeoTiff file

   for example the GMTED2010 elevation data from Nasa/USGS Earth Explorer

   NOTE: Pass the GeoTIFF file from USGS directly, dont use any image converter to create a png or jpg or so and then pass to this program,
   bcas it may lose some of the detail in the process.

* Reference colormap file

   This is optional, required only if one wants a preexisting coloring for the terrain to be used.

   for example if one is interested in having say the vegetation based coloring for the terrain,
   then one could pass the world vegetation GeoTiff file from Nasa/USGS/...


ColorMap/Texture file
-----------------------

The color map file generated by the helper script, could be either based on

a) color decided based on height/elevation (color/gray intensity ie value in elevation file given) at each location in the terrain.

   This is the default. The elevation data is divided into 4 bands

   * L0: -ve to 0 levels map to blue (corresponding to sea level in a way)

   * L1: InBetween lower part (0 to +20%) would be green (corresponding to normal ground and small hills)

   * L2: InBetween higher part (+20% to +40%) would be reddish brown or so (corresponding to tall hills and so)

   * L3: high altitude level (above +40%) would be white (corresponding to snow peaks in a way).

   The p3dterrain and hf2cm commands of the helper script handle this.

   Have forgotten the nitty gritty of how things evolved over the last few days now ;(, so need to check once again, but potentially

   If one directly calls hf2cm, then the elevation levels are handled in a absolute manner, so this would potentially map to
   sea level and below, ground and small hills, tall hill parts, snow peaks +

   However if one triggers this as part of p3dterrain command, then the elevation levels are handled in a relative to itself manner.
   In which case the height range in the image will be divided into 4 bands and colored accordingly. Which means that even a region
   with only high altitudes may also show all the 4 coloring as the case may be.


b) color based on color at same geographic position in a reference image.

   This could for example be used to color the terrain based on vegetation GeoTiff file from NASA/USGS/...

   The reference image passed needs to contain the geographic region co-ordinates corresponding to the elevation file passed.

   For this both the heightfield/elevation file as well as the reference image need to be GeoTiff images, so that the helper script
   can try to map the heightfield file to its corresponding location in the reference image.

   The mapto command of the helper script helps with this.

