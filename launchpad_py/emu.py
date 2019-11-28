from collections import deque, defaultdict

import PySimpleGUIQt as sg

from launchpad_py.launchpad import LaunchpadBase
from launchpad_py.utils import Colour

# Because Qt has different ideas about what size a button, or possibly a character, should be.
if sg.__name__ == 'PySimpleGUIQt':
    BTN_SIZE = (4, 1)
else:
    BTN_SIZE = (2, 2)


class LaunchpadEmu(LaunchpadBase):
    """
    A Launchpad emulator in Qt.
    Behaves superficially the same as the real thing, obviously not counting the music or timing stuff.
    TODO: passthrough to a real device
    """
    # type:dict[sg.Button]
    buttons = None # GUI button objects
    presses = None # queue of button presses
    values = None  # colour values

    def __init__(self):
        self.initialise()
        self.window = self.gui_setup()
        LaunchpadBase.__init__(self)
        self.gui_update(timeout=0)

    def __delete__(self):
        pass

    def initialise(self):
        self.presses = deque()
        self.buttons = {}
        self.values = defaultdict(lambda: Colour(0,0))

    def press(self, x, y, updown=None):
        """
        simulates a button press.
        TODO: permit mousedown/mouseup events to allow button holds
        TODO: for bonus points allow button sweeps with mouse held down
        """
        if x < 0 or x > 8 or y < 0 or y > 8 or (x == 8 and y == 0):
            raise ValueError("Invalid grid reference.")
        if updown is None:
            self.presses.append((x,y,True))
            self.presses.append((x,y,False))
        else:
            self.presses.append((x,y,updown))

    # --- Launchpad bits ---------------------
    def Open(self, number=0, name="Launchpad"):
        return True

    def Check(self, number=0, name="Launchpad"):
        return True

    def Close(self):
        self.close()

    def ListAll(self):
        return ['Launchpad Emulator']

    def LedCtrlXY(self, x, y, red, green ):
        if x < 0 or x > 8 or y < 0 or y > 8 or (x == 8 and y == 0):
            raise ValueError("Invalid grid reference.")
        if red < 0 or red > 3 or green < 0 or green > 3:
            raise ValueError("Invalid colour setting.")
        c = Colour(red, green)
        self.values[x,y] = c
        self.buttons[x,y].Update(text = "#", button_color = ('black', c.rgbhex()))
        self.gui_update(timeout=0)

    def LedAllOn( self, colorcode = None ):
        if colorcode == 0:
            self.Reset()
        else:
            raise NotImplementedError

    def ButtonFlush(self):
        self.presses.clear()

    def ButtonChanged(self):
        """
        also performs a sneaky, non-blocking GUI update
        """
        self.gui_update(timeout=0)
        return len(self.presses) > 0

    def ButtonStateXY(self):
        try:
            return self.presses.popleft()
        except IndexError:
            return ()

    def Reset(self):
        self.initialise()
        for xy, btn in self.buttons.items():
            btn.Update(text="#", button_color=('black', self.values[xy].rgbhex()))
        self.gui_update(timeout=0)

    def EventRaw(self):
        raise NotImplementedError

    def LedCtrlRaw(self, number, red, green):
        raise NotImplementedError

    def LedCtrlRawRapid(self, allLeds):
        raise NotImplementedError

    def LedCtrlRawRapidHome(self):
        raise NotImplementedError

    def LedCtrlAutomap(self, number, red, green):
        raise NotImplementedError

    def LedCtrlChar(self, char, red, green, offsx=0, offsy=0):
        return super.LedCtrlChar(self, char, red, green, offsx=0, offsy=0)

    def LedCtrlString(self, string, red, green, direction=None, waitms=150):
        return super.LedCtrlString(self, string, red, green, direction=None, waitms=150)

    def ButtonStateRaw(self):
        raise NotImplementedError
        return []

    # --- GUI bits ---------------------
    def round_button(self, x, y):
        btn = sg.Button('○', size=BTN_SIZE, key=(x, y), button_color=('white','brown'))
        self.buttons[x,y] = btn
        return btn

    def square_button(self, x, y):
        btn = sg.Button('□', size=BTN_SIZE, key=(x, y))
        self.buttons[x,y] = btn
        return btn

    def gui_setup(self):
        sg.change_look_and_feel('Black')  # emulate the hardware
        # All the stuff inside your window.
        layout = [
            [sg.Text('[ %s ]' % col, size=BTN_SIZE) for col in range(1, 9)],
            [self.round_button(col, 0) for col in range(8)],
        ]
        for rowid, row in enumerate(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']):
            layout += [
                [self.square_button(col, rowid+1) for col in range(8)] + [self.round_button(8, rowid+1)] + [sg.Text('[%s]' % row)]
            ]
        window = sg.Window('Launchpad Emulator', layout, finalize=True)
        return window

    def gui_update(self, timeout=0):
        """
        Event Loop to process "events" and get the "values" of the inputs
        :param timeout:
        """
        event, values = self.window.read(0)
        if event is None: # if user closes window
            self.window.close()
        elif event == sg.TIMEOUT_KEY:
            return
        else:
            self.press(*event)
            print(event, ": ", values)

    def run(self):
        while True:
            self.gui_update(timeout=None) # block

    def close(self):
        self.window.close()


if __name__ == '__main__':
    LaunchpadEmu().run()
