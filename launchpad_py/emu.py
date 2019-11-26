#!/usr/bin/env python3
#
# A Novation Launchpad control suite for Python.
#
# https://github.com/FMMT666/launchpad.py
# 
# FMMT666(ASkr) 01/2013..09/2019
# www.askrprojects.net
#
#
#
#  >>>
#  >>> NOTICE FOR SPACE USERS:
#  >>>
#  >>>  Yep, this one uses tabs. Tabs everywhere.
#  >>>  Deal with it :-)
#  >>>
#

import string
import random
import sys
import array

from pygame import midi
from pygame import time

from launchpad_py.charset import *
from launchpad_py.launchpad import *
from collections import defaultdict

########################################################################################
### CLASS Launchpad
###
### For 2-color Launchpads with 8x8 matrix and 2x8 top/right rows
########################################################################################
class LaunchpadEmu( LaunchpadBase ):
        # LED AND BUTTON NUMBERS IN XY MODE (X/Y)
        #
        #   0   1   2   3   4   5   6   7      8   
        # +---+---+---+---+---+---+---+---+ 
        # |   |1/0|   |   |   |   |   |   |         0
        # +---+---+---+---+---+---+---+---+ 
        # 
        # +---+---+---+---+---+---+---+---+  +---+
        # |0/1|   |   |   |   |   |   |   |  |   |  1
        # +---+---+---+---+---+---+---+---+  +---+
        # |   |   |   |   |   |   |   |   |  |   |  2
        # +---+---+---+---+---+---+---+---+  +---+
        # |   |   |   |   |   |5/3|   |   |  |   |  3
        # +---+---+---+---+---+---+---+---+  +---+
        # |   |   |   |   |   |   |   |   |  |   |  4
        # +---+---+---+---+---+---+---+---+  +---+
        # |   |   |   |   |   |   |   |   |  |   |  5
        # +---+---+---+---+---+---+---+---+  +---+
        # |   |   |   |   |4/6|   |   |   |  |   |  6
        # +---+---+---+---+---+---+---+---+  +---+
        # |   |   |   |   |   |   |   |   |  |   |  7
        # +---+---+---+---+---+---+---+---+  +---+
        # |   |   |   |   |   |   |   |   |  |8/8|  8
        # +---+---+---+---+---+---+---+---+  +---+
        def __init__(self):
            LaunchpadBase.__init__(self)
            self.grid = defaultdict(lambda: (0,0),)
        def __delete__( self ):
            pass
        def Open( self, number = 0, name = "Launchpad" ):
            return True
        def Check( self, number = 0, name = "Launchpad" ):
            return True
        def Close( self ):
            return
        def ListAll( self ):
            return ['Launchpad Emulator']
        def ButtonFlush( self ):
            return
        def EventRaw( self ):
            return []
        #-------------------------------------------------------------------------------------
        #-- reset the Launchpad
        #-- Turns off all LEDs
        #-------------------------------------------------------------------------------------
        def Reset( self ):
            self.grid.clear()
        #-------------------------------------------------------------------------------------
        #-- Controls a grid LED by its raw <number>; with <green/red> brightness: 0..3
        #-- For LED numbers, see grid description on top of class.
        #-------------------------------------------------------------------------------------
        def LedCtrlRaw( self, number, red, green ):
            raise NotImplementedError
        #-------------------------------------------------------------------------------------
        #-- Controls a grid LED by its coordinates <x> and <y>  with <green/red> brightness 0..3
        #-------------------------------------------------------------------------------------
        def LedCtrlXY( self, x, y, red, green ):
            if x < 0 or x > 8 or y < 0 or y > 8 or (x == 8 and y == 0):
                raise ValueError( "Invalid grid reference." )
            if red < 0 or red > 3 or green < 0 or green > 3:
                raise ValueError( "Invalid colour setting." )
            self.grid[(x,y)] = (red,green)
        #-------------------------------------------------------------------------------------
        #-- Sends a list of consecutive, special color values to the Launchpad.
        #-- Only requires (less than) half of the commands to update all buttons.
        #-- [ LED1, LED2, LED3, ... LED80 ]
        #-- First, the 8x8 matrix is updated, left to right, top to bottom.
        #-- Afterwards, the algorithm continues with the rightmost buttons and the
        #-- top "automap" buttons.
        #-- LEDn color format: 00gg00rr <- 2 bits green, 2 bits red (0..3)
        #-- Function LedGetColor() will do the coding for you...
        #-- Notice that the amount of LEDs needs to be even.
        #-- If an odd number of values is sent, the next, following LED is turned off!
        #-- REFAC2015: Device specific.
        #-------------------------------------------------------------------------------------
        def LedCtrlRawRapid( self, allLeds ):
            raise NotImplementedError
        #-------------------------------------------------------------------------------------
        #-- "Homes" the next LedCtrlRawRapid() call, so it will start with the first LED again.
        #-------------------------------------------------------------------------------------
        def LedCtrlRawRapidHome( self ):
            raise NotImplementedError
        #-------------------------------------------------------------------------------------
        #-- Controls an automap LED <number>; with <green/red> brightness: 0..3
        #-- NOTE: In here, number is 0..7 (left..right)
        #-------------------------------------------------------------------------------------
        def LedCtrlAutomap( self, number, red, green ):
            raise NotImplementedError
        #-------------------------------------------------------------------------------------
        #-- all LEDs on
        #-- <colorcode> is here for backwards compatibility with the newer "Mk2" and "Pro"
        #-- classes. If it's "0", all LEDs are turned off. In all other cases turned on,
        #-- like the function name implies :-/
        #-------------------------------------------------------------------------------------
        def LedAllOn( self, colorcode = None ):
                if colorcode == 0:
                    self.Reset()
                else:
                    raise NotImplementedError
        #-------------------------------------------------------------------------------------
        #-- Sends character <char> in colors <red/green> and lateral offset <offsx> (-8..8)
        #-- to the Launchpad. <offsy> does not have yet any function
        #-------------------------------------------------------------------------------------
        def LedCtrlChar( self, char, red, green, offsx = 0, offsy = 0 ):
            return super.LedCtrlChar( self, char, red, green, offsx = 0, offsy = 0 )
        #-------------------------------------------------------------------------------------
        #-- Scroll <string>, in colors specified by <red/green>, as fast as we can.
        #-- <direction> specifies: -1 to left, 0 no scroll, 1 to right
        #-- The delays were a dirty hack, but there's little to nothing one can do here.
        #-- So that's how the <waitms> parameter came into play...
        #-- NEW   12/2016: More than one char on display \o/
        #-- IDEA: variable spacing for seamless scrolling, e.g.: "__/\_"
        #-------------------------------------------------------------------------------------
        def LedCtrlString( self, string, red, green, direction = None, waitms = 150 ):
            return super.LedCtrlString( self, string, red, green, direction = None, waitms = 150 )
        #-------------------------------------------------------------------------------------
        #-- Returns True if a button event was received.
        #-------------------------------------------------------------------------------------
        def ButtonChanged( self ):
            return True
        #-------------------------------------------------------------------------------------
        #-- Returns the raw value of the last button change as a list:
        #-- [ <button>, <True/False> ]
        #-------------------------------------------------------------------------------------
        def ButtonStateRaw( self ):
            return []
            raise NotImplementedError
        #-------------------------------------------------------------------------------------
        #-- Returns an x/y value of the last button change as a list:
        #-- [ <x>, <y>, <True/False> ]
        #-------------------------------------------------------------------------------------
        def ButtonStateXY( self ):
            return [3,4,True]
            raise NotImplementedError

        def cellvalue(self, x, y):
            """
            Prints out a representation of a cell value.
            TODO: use ANSI colours.
            """
            if x == 8 and y == 0:
                return "--"
            (r, g) = self.grid[(x,y)]
            return "%s%s" % (r, g)

        def __repr__(self):
            """
            Prints out a representation of the board.
            """
            for y in range(9):
                print("+--+--+--+--+--+--+--+--+--+")
                print("|"+"|".join([self.cellvalue(x,y) for x in range(9)])+"|")
            print("+--+--+--+--+--+--+--+--+--+")
