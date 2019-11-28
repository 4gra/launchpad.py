#!/usr/bin/env python3
from launchpad_py.utils import *
import random
from time import sleep


class Palette(dict):
    # hard-coded palette, ordered to be pretty
    palette = {
        (0, 0): (0, 0),  #
        (1, 0): (0, 0),  #
        (2, 0): (0, 0),  #
        (3, 0): (0, 0),  #
        (4, 0): (0, 0),  #
        (5, 0): (0, 0),  #
        (6, 0): (0, 0),  #
        (7, 0): (0, 0),
        #    (8,1) : (0,0), #
        #    (8,2) : (0,0), #
        #    (8,3) : (0,0), #
        #    (8,4) : (0,0), #
        #    (8,5) : (0,0), #
        #    (8,6) : (0,0), #
        #    (8,7) : (0,0), #
        #    (8,8) : (0,0),
    }

    selected = None
    held = 0
    painted = False
    blink = False
    BLINK_TIME = 15
    swaps = None

    def __init__(self, lp):
        self.blink = self.BLINK_TIME
        self.update(self.palette)
        self.lp = lp
        self.paint()
        super(Palette, self).__init__()

    # def swap(self):
    #     self.swaps += [self.selected]

    def paint(self, blink=None):
        if not self.painted:
            i = 0
            for k, v in self.palette.items():
                i += 1
                (x, y) = k
                (r, g) = v
                self.lp.LedCtrlXY(x, y, r, g)
            self.painted = True
        if self.selected and self.selected != (0, 0) and self.selected != self.painted:
            if self.held:
                self.held += 1
            (x, y) = self.selected
            # if self.held > 50:
            #    self[(self.selected)] = (0,0)
            if blink is not None:
                self.blink = blink
            if self.blink > 0:
                (r, g) = self[self.selected]
                self.blink -= 1
            else:
                (r, g) = tweak(self[self.selected])
                self.blink = self.BLINK_TIME
                print(" (blink %d)" % self.held)
            self.lp.LedCtrlXY(x, y, r, g)

    def unselect(self, x, y):
        self.held = 0
        self.paint(10)
        return self[(x, y)]

    def select(self, x, y):
        self.selected = (x, y)
        self.held = 1
        self.paint(5)
        return self[self.selected]


class Score(Palette):
    empty = Colour(0, 0)
    point = Colour(0, 3)

    def __init__(self, lp):
        self.count = 0
        self.lastcount = 0
        super(Score, self).__init__(lp)

    def paint(self, blink=False):
        if self.lastcount != self.count:
            self.lastcount = self.count
            print("Score is %s!" % self.count)
        i = 0
        for (k, v) in self.items():
            (x, y) = k
            if blink is False and i < self.count:
                self.lp.LedCtrlXY(x, y, self.point.r, self.point.g)
            else:
                self.lp.LedCtrlXY(x, y, self.empty.r, self.empty.g)
            i += 1

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


def game_loop():
    with LaunchpadPlease() as lp:
        # palette = Palette(lp)
        score = Score(lp)
        field = Colour(0, 0)
        squash = Colour(3, 3)
        mole = Colour(3, 0)
        hill = Colour(1, 0)
        easy_loc = (8, 8)
        mpos = (None, None)  # mole position
        squashed = False
        easy = None
        ticks = 0  # since last squash

        while True:
            score.paint()
            # make a mole
            mchance = (random.choice(range(100 - ticks)) < 1)
            if mchance:
                ticks = 0
                if mpos[0] is not None:
                    lp.LedCtrlXY(*mpos, hill.r, hill.g)
                print("Mole at %s, %s!" % mpos)
                mpos = (random.choice(range(8)),
                        random.choice(range(1, 9)))
                lp.LedCtrlXY(*mpos, mole.r, mole.g)
                if squashed:
                    squashed = False
                else:
                    if not easy:
                        score.dec()
            else:
                ticks += 1

            sleep(0.1)

            if not lp.ButtonChanged():
                continue

            # process all buttons in one go
            while True:
                if score.count >= 8:
                    score.win()
                    fill(lp, field.r, field.g)
                try:
                    (x, y, pressed) = lp.ButtonStateXY()  # raises ValueError when state is None
                    print("+" if pressed else "-", x, y)
                    # (always on press; discard release)
                    # colour the easy button
                    if easy is None or pressed and (x, y) == easy_loc:
                        print("easy mode: %s" % easy)
                        easy = not easy
                        colour = OFF if easy else RED
                        print("painting: easy_loc, colour, easy")
                        lp.LedCtrlXY(*easy_loc, *colour)
                    # handle squashing or missing
                    elif pressed and (x, y) not in score:
                        if (x, y) == mpos:
                            lp.LedCtrlXY(x, y, squash.r, squash.g)
                            if not squashed:
                                score.inc()
                                squashed = True
                        else:
                            lp.LedCtrlXY(x, y, field.r, field.g)
                            if not easy:
                                score.dec()
                        score.paint()
                except ValueError:  # when state == None
                    break


if __name__ == '__main__':
    game_loop()
