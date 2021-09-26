##############
FSim Readme
##############
Author: HanishKVC
Version: v20210927IST0302

Intro
########

A simple dumb flight sim with a futuristic all degree freedom space ship mode for now.

Usage
=======

Cmdline
----------

./fsim <options>

The supported options are

* --terrain <base_filename>

* --topview


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

  + i : rotate up

  + k : rotate down

  + j : rotate left

  + l : rotate right

  + u : tilt left

  + o : tilt right


Terrain
##########

It allows height fields to be used as the terrain.

There is a helper script to which one can pass the USGS earth explorer GMTED2010 elevation data and inturn it will generate heightfield and colormap files which can be used by this program.


