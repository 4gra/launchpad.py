#!/usr/bin/env python3
"""
A tiny drawing programme and a fun programming toy.

Copyright (C) 2019, https://github.com/4gra/launchpad.py
Based entirely on lovely work of https://github.com/FMMT666/launchpad.py

This program comes with ABSOLUTELY NO WARRANTY; for details see included LICENCE.
This is free software, and you are welcome to redistribute it under certain
conditions; view the included file LICENCE for details.
"""
from launchpad_py.utils import *
from time import sleep

# replay functions
from datetime import datetime, timedelta
 
class Palette(dict):
    # hard-coded palette, ordered to be pretty
    palette = {
        (0, 0): (0, 0),  #
        (1, 0): (0, 1),  #
        (2, 0): (0, 2),  #
        (3, 0): (0, 3),  #
        (4, 0): (1, 0),  #
        (5, 0): (2, 0),  #
        (6, 0): (3, 0),  #
        (7, 0): (3, 3),

        (8, 1): (3, 1),  #
        (8, 2): (2, 1),  #
        (8, 3): (3, 2),  #
        (8, 4): (1, 3),  #
        (8, 5): (1, 2),  #
        (8, 6): (2, 3),  #
        (8, 7): (2, 2),  #
        (8, 8): (1, 1),
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
        self.start_time = datetime.now()
        print("# START: ", str(self.start_time))

    # def swap(self):
    #    self.swaps += [ self.selected ]

    def paint(self, blink=None):
        if not self.painted:
            i = 0
            for k, v in self.palette.items():
                i += 1
                self.lp.LedCtrlXY(*k, *v)
            self.painted = True
        if self.selected and self.selected != self.painted:
            if self.held:
                self.held += 1
            if self.held > 50:
                self.held = 0
                fill(self.lp, *self[self.selected])
            if self.selected != (0, 0):
                if blink is not None:
                    self.blink = blink
                if self.blink > 0:
                    colour = self[self.selected]
                    self.blink -= 1
                else:
                    colour = tweak(self[self.selected])
                    self.blink = self.BLINK_TIME
                    #print(" (blink %d)" % self.held)
                self.lp.LedCtrlXY(*self.selected, *colour)

    def unselect(self, x, y):
        self.held = 0
        self.paint(10)
        return self[(x, y)]

    def select(self, x, y):
        self.selected = (x, y)
        self.held = 1
        self.paint(5)
        return self[self.selected]


def game_loop():
    with LaunchpadPlease() as lp:
        palette = Palette(lp)
        timer = Timer(lp)
        colour = (0, 0)
        # print(lp)
        while True:
            timer.inc()
            palette.paint()
            if not lp.ButtonChanged():
                sleep(0.02)
            else:
                # process all buttons in one go
                while True:

                    try:
                        (x, y, v) = lp.ButtonStateXY()  # raises ValueError when state is None
                        diff = str(datetime.now() - palette.start_time)
                        print(diff, "+" if v else "-", x, y)
                        if (x, y) in palette:
                            if v:
                                colour = palette.select(x, y)
                            else:
                                colour = palette.unselect(x, y)
                            print("# Get", x, y, colour)
                        elif v:  # on press; discard release
                            print("# Set", x, y, colour)  # TODO: print in colour!
                            lp.LedCtrlXY(x, y, *colour)
                    except ValueError:  # when state == None
                        break


if __name__ == '__main__':
    game_loop()
