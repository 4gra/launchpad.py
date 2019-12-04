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
import mpd
from time import sleep

class Radio:
    def __init__(self):
        self.client = mpd.MPDClient(use_unicode=True)
        self.client.connect("localhost", 6600)

    def play(self, station=None):
        #for entry in self.client.lsinfo("/"):
        #    print("%s" % entry)
        #for key, value in self.client.status().items():
        #    print("%s: %s" % (key, value))
        if station:
            self.client.clear()
            self.client.load(station)
            self.client.play()
        else:
            self.client.stop()
        # mpc clear; mpc load BBC_Radio_3; mpc play

    #client.close()


class Palette(dict):
    # hard-coded palette, ordered to be pretty
    palette = {
        (0, 0): (0, 0),  #
        (1, 0): (0, 0),  #
        (2, 0): (0, 1),  #
        (3, 0): (0, 1),  #
        (4, 0): (0, 0),  #
        (5, 0): (0, 1),  #
        (6, 0): (0, 0),  #
        (7, 0): (0, 0),
    }

    stations = {
        0:  None,
        2:  'BBC_Radio_3',
        3:  'BBC_Radio_4',
        5:  'BBC_6_Music'
    }

    selected = None
    painted = False
    station = None

    def __init__(self, lp):
        self.update(self.palette)
        self.lp = lp
        self.paint()

    def paint(self):
        if not self.painted:
            i = 0
            for k, v in self.palette.items():
                i += 1
                if self.selected and k == self.selected:
                    #colour = tweak(self[self.selected])
                    colour = (0,3)
                else:
                    self.lp.LedCtrlXY(*k, *v)
            self.painted = True

    def unselect(self, x, y):
        self.held = 0
        self.paint()
        return self[(x, y)]

    def select(self, x, y):
        if self.selected == (x,y):
            return False
        old = self.selected
        self.selected = (x, y)
        self.held = 1
        self.paint()
        try:
            self.station = self.stations[x]
            return self.station
        except:
            return None


def game_loop():
    with LaunchpadPlease() as lp:
        palette = Palette(lp)
        radio = Radio()
        timer = Timer(lp)
        colour = (0, 0)
        # print(lp)
        while True:
            timer.inc()
            palette.paint()
            if not lp.ButtonChanged():
                sleep(0.5)
            else:
                # process all buttons in one go
                while True:

                    try:
                        (x, y, v) = lp.ButtonStateXY()  # raises ValueError when state is None
                        print("+" if v else "-", x, y)
                        if (x, y) in palette:
                            if v:
                                changed = palette.select(x, y)
                                if changed != False:
                                    radio.play(palette.station)
                    except ValueError:  # when state == None
                        break


if __name__ == '__main__':
    game_loop()
