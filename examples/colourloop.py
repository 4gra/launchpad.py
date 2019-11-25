#!/usr/bin/env python3
import launchpad_py as launchpad
from time import sleep

#colours = {
#    (0,0): #
#    (0,1): # 
#    (0,2): #
#    (0,3): #
#    (1,0): #
#    (2,0): #
#    (3,0): #
#    (3,3):
#
#    (3,1): #
#    (2,1): #
#    (3,2): #
#    (1,3): #
#    (1,2): #
#    (2,3): #
#    (2,2): #
#    (1,1):
#}

class LaunchpadPlease():
    """
    Makes a launchpad connection, and handles setup/shutdown.
    Opens an emulator (LaunchpadEmu) if none is available.
    """
    def __enter__(self):
        try:
            self.lp = launchpad.Launchpad()
            self.lp.Open()
            self.lp.ButtonFlush()
        except:
            self.lp = launchpad.LaunchpadEmu()
        return self.lp

    def __exit__(self, type, value, traceback):
        print("exiting with %s, %s, %s" % (type, value, traceback))
        #self.lp.Reset() # turn all LEDs off
        self.lp.Close() # close the Launchpad (will quit with an error due to a PyGame bug)


class Colour:
    def __init__(self, r, g, o=1):
        self.r = r
        self.g = g
        self.o = o

    def tweak(self):
        return tweak((self.r, self.g))

    def colour(self):
        return (r, g)

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


class Palette(dict):

    # hard-coded palette, ordered to be pretty
    palette = {
        (0,0) : (0,0), #
        (1,0) : (0,1), # 
        (2,0) : (0,2), #
        (3,0) : (0,3), #
        (4,0) : (1,0), #
        (5,0) : (2,0), #
        (6,0) : (3,0), #
        (7,0) : (3,3),

        (8,1) : (3,1), #
        (8,2) : (2,1), #
        (8,3) : (3,2), #
        (8,4) : (1,3), #
        (8,5) : (1,2), #
        (8,6) : (2,3), #
        (8,7) : (2,2), #
        (8,8) : (1,1),
    }

    selected = None
    held = 0
    painted = False
    blink = False
    BLINK_TIME = 15

    def __init__(self, lp):
        self.blink = self.BLINK_TIME
        self.update(self.palette)
        self.lp = lp
        self.paint()

    def swap(self):
        self.swaps += [ self.selected ]

    def paint(self, blink=None):
        if not self.painted:
            i = 0
            for k, v in self.palette.items():
                i+=1
                (x, y) = k
                (r, g) = v
                self.lp.LedCtrlXY(x,y,r,g)
            self.painted = True
        if self.selected and self.selected != (0,0) and self.selected != self.painted:
            if self.held:
                self.held += 1
            (x, y) = self.selected
            #if self.held > 50:
            #    self[(self.selected)] = (0,0)
            if blink != None:
                self.blink = blink
            if self.blink > 0:
                (r, g) = self[(self.selected)]
                self.blink -= 1
            else:
                (r, g) = tweak(self[(self.selected)])
                self.blink = self.BLINK_TIME
                print(" (blink %d)" % self.held)
            self.lp.LedCtrlXY(x,y,r,g)

    def unselect(self, x, y):
        self.held = 0
        self.paint(10)
        return self[(x,y)]

    def select(self, x, y):
        self.selected = (x,y)
        self.held = 1
        self.paint(5)
        return self[(self.selected)]

if __name__ == '__main__':
    with LaunchpadPlease() as lp:
        palette = Palette(lp)
        (r, g) = (0,0)
        print(lp)
        while True:
            palette.paint()
            if not lp.ButtonChanged():
                sleep(0.02)
            else:
                # process all buttons in one go
                while True: 

                    try:
                        (x, y, v) = lp.ButtonStateXY() # raises ValueError when state is None
                        print("+" if v else "-", x, y)
                        if (x, y) in palette:
                            if v:
                                (r, g) = palette.select(x, y)
                            else:
                                (r, g) = palette.unselect(x, y)
                            print("Get", x, y, r, g)
                        elif v: # on press; discard release
                            print("Set", x, y, r, g) # TODO: print in colour
                            lp.LedCtrlXY(x, y, r, g)
                    except ValueError: # when state == None
                        break
