#!/usr/bin/env python3
import launchpad_py as launchpad
import random
from time import sleep

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
        (1,0) : (0,0), # 
        (2,0) : (0,0), #
        (3,0) : (0,0), #
        (4,0) : (0,0), #
        (5,0) : (0,0), #
        (6,0) : (0,0), #
        (7,0) : (0,0),

        (8,1) : (0,0), #
        (8,2) : (0,0), #
        (8,3) : (0,0), #
        (8,4) : (0,0), #
        (8,5) : (0,0), #
        (8,6) : (0,0), #
        (8,7) : (0,0), #
        (8,8) : (0,0),
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

class Score(Palette):

    empty = Colour(0,0)
    point = Colour(0,3)

    def __init__(self, lp):
        self.count = 0
        super( Score, self ).__init__(lp)

    def paint(self, blink=False):
        print("Score is %s" % self.count)
        i = 0
        for (k, v) in self.items():
            (x, y) = k
            if blink == False and i < self.count:
                self.lp.LedCtrlXY(x,y,self.point.r,self.point.g)
            else:
                self.lp.LedCtrlXY(x,y,self.empty.r,self.empty.g)
            i+=1

    def inc(self):
        self.count += 1
        self.paint()

    def dec(self):
        if self.count > 0:
            self.count -= 1
        self.paint()

    def win(self):
        # blink for N times, then reset the board
        blink = 5
        while blink > 0:
            self.paint(True)
            sleep(0.25)
            self.paint(False)
            sleep(0.25)
            blink -= 1
        self.count = 0


if __name__ == '__main__':
    with LaunchpadPlease() as lp:
        #palette = Palette(lp)
        score = Score(lp)
        field = Colour(0,0)
        squash = Colour(3,3)
        mole = Colour(3, 0)
        hill = Colour(1, 0)
        (mx, my) = (None, None) # mole position
        squashed = False

        print(lp)
        while True:
            #palette.paint()
            score.paint()
            # make a mole
            mchance = ( random.choice(range(80)) < 1 )
            if mchance:
                if mx != None:
                    lp.LedCtrlXY(mx, my, hill.r, hill.g)
                print("Mole at %s, %s!" % (mx, my))
                mx = random.choice(range((8)))
                my = random.choice(range(1,9))
                lp.LedCtrlXY(mx, my, mole.r, mole.g)
                if squashed:
                    squashed = False
                else:
                    score.dec()

            sleep(0.02)
            if not lp.ButtonChanged():
                sleep(0.02)

            # process all buttons in one go
            while True: 
                if score.count >= 8:
                    score.win()
                    for x in range(8):
                        for y in range(1,9):
                            lp.LedCtrlXY(x, y, field.r, field.g)
                try:
                    (x, y, v) = lp.ButtonStateXY() # raises ValueError when state is None
                    print("+" if v else "-", x, y)
                    # on press; discard release
                    if v and (x, y) not in score:
                        if (x,y) == (mx, my):
                            lp.LedCtrlXY(x, y, squash.r, squash.g)
                            if not squashed:
                                score.inc()
                                squashed = True
                        else:
                            lp.LedCtrlXY(x, y, field.r, field.g)
                            score.dec()
                        score.paint()
                except ValueError: # when state == None
                    break

