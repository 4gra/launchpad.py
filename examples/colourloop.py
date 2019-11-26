#!/usr/bin/env python3
from launchpad_py.utils import *
from time import sleep

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

    #def swap(self):
    #    self.swaps += [ self.selected ]

    def paint(self, blink=None):
        if not self.painted:
            i = 0
            for k, v in self.palette.items():
                i+=1
                self.lp.LedCtrlXY(*k, *v)
            self.painted = True
        if self.selected and self.selected != self.painted:
            if self.held:
                self.held += 1
            if self.held > 50:
                self.held = 0
                self.lp.fill(*self[self.selected])
            if self.selected != (0,0):
                if blink != None:
                    self.blink = blink
                if self.blink > 0:
                    colour = self[(self.selected)]
                    self.blink -= 1
                else:
                    colour = tweak(self[(self.selected)])
                    self.blink = self.BLINK_TIME
                    print(" (blink %d)" % self.held)
                self.lp.LedCtrlXY(*self.selected, *colour)

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
        timer = Timer(lp)
        colour = (0,0)
        #print(lp)
        while True:
            timer.inc()
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
                                colour = palette.select(x, y)
                            else:
                                colour = palette.unselect(x, y)
                            print("Get", x, y, colour)
                        elif v: # on press; discard release
                            print("Set", x, y, colour) # TODO: print in colour
                            lp.LedCtrlXY(x, y, *colour)
                    except ValueError: # when state == None
                        break
