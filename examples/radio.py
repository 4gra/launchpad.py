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
try:
    from pclk_mn10 import stub as pclk
except ImportError:
    print("pclk-mn10 not found, but that's OK")
    class pclk:
        def setup_pipes():
            pass
        def run(args):
            pass


stations = {
    0:  'BBC_Radio_1',
    1:  'BBC_Radio_2',
    2:  'BBC_Radio_3',
    3:  'BBC_Radio_4',
    5:  'BBC_6_Music',
    7:  None,
}

class Radio:
    def __init__(self):
        self.patience = 100
        self.client = mpd.MPDClient(use_unicode=True)
        self.reconnect()

    def reconnect(self):
        if self.client:
            try:
                client.close()
            except:
                pass
        try:
            self.client.connect("localhost", 6600)
            return True
        except mpd.base.ConnectionError:
            return False

    def play(self, station=None):
        #for entry in self.client.lsinfo("/"):
        #    print("%s" % entry)
        #for key, value in self.client.status().items():
        #    print("%s: %s" % (key, value))
        while self.patience:
            try:
                if station:
                    pclk.run(['on','TAPE'])
                    self.client.clear()
                    self.client.load(station)
                    self.client.play()
                else:
                    self.client.stop()
                    pclk.run(['off'])
                self.patience = 100
                return
            except mpd.base.ConnectionError:
                self.patience -= 1
                self.reconnect()
        raise IOError("ran out of patience trying to contact MPD")

        # mpc clear; mpc load BBC_Radio_3; mpc play



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
                (x, y) = k
                print(self.selected, k)
                if self.selected and self.selected == k:
                    #colour = tweak(self[self.selected])
                    colour = (1, 1)
                elif x in stations and stations[x]:
                    colour = (0, 1)
                else:
                    colour = (0, 0)
                self.lp.LedCtrlXY(*k, *colour)
            self.painted = True

    def unselect(self, x, y):
        self.held = 0
        self.paint()
        return self[(x, y)]

    def select(self, x, y):
        if self.selected == (x,y):
            return False
        self.painted = False
        self.selected = (x, y)
        self.held = 1
        self.paint()
        try:
            self.station = stations[x]
            return self.station
        except:
            return None


def game_loop():
    with LaunchpadPlease(reset_on_close=True) as lp:
        pclk.setup_pipes()
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
    pclk.run(['off'])
