#!/usr/bin/env python3
import launchpad_py as launchpad
from collections import defaultdict

OFF    = (0,0)
#    (1,0): #
#    (2,0): #
RED    = (3,0)
YELLOW = (3,3)
#    (0,1): # 
#    (0,2): #
GREEN  = (0,3)
#    (3,1): #
#    (2,1): #
#    (3,2): #
#    (1,3): #
#    (1,2): #
#    (2,3): #
#    (2,2): #
#    (1,1):

def tweak(rg):
    """
    makes the most minimally visible change to a colour.
    there's a mathematically neat way of doing this that evades me right now
        (i.e. don't change r/g ratios except if one of them is zero.)
    """
    (r, g) = rg
    if r == 0 and g == 0:
        return (0,0)
    elif r == 1 and g == 1:
        return (2,2)
    elif r == 0:
        if g == 1:
            g+=1
        else:
            g -= 1
    elif g == 0:
        if r == 1:
            r += 1
        else:
            r -= 1
    else:
        r -= 1
        g -= 1
    return (r, g)

class Colour:
    """
    colour class.
    experimental opacity or something?
    """
    def __init__(self, r, g, o=1):
        self.r = r
        self.g = g
        self.o = o

    def tweak(self):
        return tweak((self.r, self.g))

    def colour(self):
        return (r, g)


class CachingLaunchpad(launchpad.Launchpad):
    led = defaultdict(lambda: (0,0)) # LED states
    btn = {} # button states??
    PRINT_CTR = None
    ctr = 0

    def __init__(self, printctr=500):
        self.printctr = printctr
        self.ctr = 0
        super(CachingLaunchpad, self).__init__()

    def fill(self, r, g, every_led=False):
        """fills the board with a single colour"""
        if every_led:
            raise NotImplementedError
        for x in range(8):
            for y in range(1,9):
                self.LedCtrlXY(x, y, r, g)

    def LedCtrlXY(self, x, y, r, g):
        #self.led[(x,y)] = Colour(r,g)
        self.led[(x, y)] = (r,g)
        if self.PRINT_CTR != None and self.ctr > self.PRINT_CTR:
            self.ctr = 0
            print(self)
        else:
            self.ctr += 1
        return super(CachingLaunchpad, self).LedCtrlXY(x, y, r, g)

    def LedGetXY(self, x, y):
        return self.led[(x, y)]

    def __getitem__(self, xy):
        return self.LedGetXY(*xy)

    def cellvalue(self, x, y):
        """
        Prints out a representation of a cell value.
        TODO: use ANSI colours.
        """
        if x == 8 and y == 0:
            return "--"
        (r, g) = self[(x,y)]
        return "%s%s" % (r, g)

    def __repr__(self):
        """
        Prints out a representation of the board.
        """
        out = "\n"
        for y in range(9):
            out += "+--+--+--+--+--+--+--+--+--+\n"
            out += ("|"+"|".join([self.cellvalue(x,y) for x in range(9)])+"|\n")
        out += ("+--+--+--+--+--+--+--+--+--+\n")
        return out

class LaunchpadPlease():
    """
    Makes a launchpad connection, and handles setup/shutdown.
    Opens an emulator (LaunchpadEmu) if none is available.
    """
    def __init__(self, reset_on_close=False):
        self.reset_on_close = reset_on_close
    def __enter__(self):
        try:
            self.lp = CachingLaunchpad()
            self.lp.Open()
            self.lp.ButtonFlush()
        except:
            self.lp = LaunchpadEmu()
        return self.lp

    def __exit__(self, type, value, traceback):
        print("exiting with %s, %s, %s" % (type, value, traceback))
        if self.reset_on_close:
            self.lp.Reset() # turn all LEDs off
        self.lp.Close() # close the Launchpad (will quit with an error due to a PyGame bug)


class Timer():
    """
    something something a timer
    """
    SLEEP_TIME = 5000
        
    def __init__(self, lp):
        self.ticks = 0
        self.lp = lp
        self.sleep = False
        self.blink = False

    def draw(self):
        """
        sets sleep mode.
        """
        if not self.sleep:
            return
        # blank screen
        # blink

    def inc(self):
        self.ticks += 1
        if self.ticks >= self.SLEEP_TIME:
            self.sleep = True

