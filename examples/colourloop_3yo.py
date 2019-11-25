#!/usr/bin/env python3
import launchpad_py as launchpad
from time import sleep

class LaunchpadPlease():
    
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


def set_palette(lp):
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
    i = 0
    for k, v in palette.items():
        print(k, v)
        i+=1
        (x, y) = k
        (r, g) = v
        print("%s, %s = %s, %s" % (x, y, r, g))
        lp.LedCtrlXY(x,y,r,g)
    return palette

if __name__ == '__main__':
    with LaunchpadPlease() as lp:
        palette = set_palette(lp)
        (r, g) = (0,0)
        print(lp)
        while True:
            #paletteStrobe()
            if not lp.ButtonChanged():
                sleep(0.1)
            else:
                (r, g) = (0,0)
                while True:
                    try:
                        (x, y, v) = lp.ButtonStateXY()
                        print("Seen", x, y, v)
                        if v:
                            if (x, y) in palette:
                                (r, g) = palette[(x,y)]
                                #print("Get", x, y, r, g)
                            else:
                                #print("Set", x, y, r, g) # TODO: print in colour
                                lp.LedCtrlXY(x, y, r, g)
                    except ValueError:
                        pass
