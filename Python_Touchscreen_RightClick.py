"""
Zyell's Python Script for adding 1 & 2 finger multitouch gestures to implement
a right click option with Touchscreens in the Ubuntu unity environment.

This is implemented with the evdev Python library on an ELAN touchscreen.

Currently implements 2 types of right click options:
1 finger long touch: Timeout of 0.7 seconds, movement cancels action
2 finger tap: movement cancels action

Modified by gevasiliou (GV) , October 2016
"""

from evdev import InputDevice, ecodes, UInput, list_devices
from pymouse import PyMouse  #GV added. Requires pymouse and python-xlib libraries
import datetime


class TrackedEvent(object):

    """
    Class for multitouch event tracking.
    Track position, movement, slots used (total number of fingers in gesture),
    timing of long presses, and event completion.
    """

    def __init__(self):
        """ Initialize tracking attributes. """
        self.position = {'ABS_X': None, 'ABS_Y': None}
        self.slots = []
        self.fingers = 0
        self.total_event_fingers = 0
        self.discard = 0
        self.moved = 0
        self.track_start = None
        self.click_delay = 0.7

    def add_finger(self, slot):
        """  Add a detected finger. """
        if slot not in self.slots:
            self.fingers += 1
            self.slots.append(slot)
        if self.total_event_fingers < self.fingers:
            self.total_event_fingers = self.fingers

    def remove_fingers(self):
        """ Remove detected finger upon release. """
        if self.total_event_fingers == self.fingers:
            if self.total_event_fingers == 0:
                self.total_event_fingers = 1
            print('Total Fingers used: ', self.total_event_fingers)
        self.fingers -= 1

        if (self.fingers == 0 and
                self.total_event_fingers == 2 and
                self.moved == 0):
            self._initiate_right_click()

        elif ((self.fingers == 0 or self.fingers == -1) and
                self.total_event_fingers == 1 and
                self.moved == 0):
            self._internal_timing()

        if self.fingers == 0 or self.fingers == -1:
            self.discard = 1

    def position_event(self, event_code, value):
        """ tracks position to track movement of fingers """
        if self.position[event_code] is None:
            self.position[event_code] = value
        else:
            #print('movement detected....')  
            #print('position event old value=', self.position[event_code])
            #print('position event new value=', value)
            OldValue = self.position[event_code]  #gv added
            NewValue = value  #gv added
            diff = OldValue - NewValue	#gv added
            #print('difference=',diff)
            if abs(diff) > 50:  #gv added :allows a movement of +/- 50 pixels before to cancel right click 
                print('movement more than treshold, cancelling right click')
                self._moved_event()

    def trackit(self):
        """ start timing for long press """
        self.track_start = datetime.datetime.now()

    def _moved_event(self):
        """ movement detected. """
        self.moved = 1

    def _internal_timing(self):
        """ Internal method for determining long press time right clicking. """
        if self.track_start is not None:
            elapsed = datetime.datetime.now() - self.track_start
            if elapsed.total_seconds() > self.click_delay:
                self._initiate_right_click()

    def _initiate_right_click(self):
        """ Internal method for initiating a right click at touch point. """
        #capabilities = {ecodes.EV_ABS: (ecodes.ABS_X, ecodes.ABS_Y),
        #                ecodes.EV_KEY: (ecodes.BTN_LEFT, ecodes.BTN_RIGHT)}
        #with UInput(capabilities) as ui:
        #    ui.write(ecodes.EV_ABS, ecodes.ABS_X, 0)
        #    ui.write(ecodes.EV_ABS, ecodes.ABS_Y, 0)
        #    ui.write(ecodes.EV_KEY, ecodes.BTN_RIGHT, 1)
        #    ui.write(ecodes.EV_KEY, ecodes.BTN_RIGHT, 0)
        #    ui.syn()
        """ 
        GV: Pytho-EvDev method "ui.write" did not work on my ELAN Screen - usb connected.
        On the other hand the use of pymouse worked ok.
        """
        m = PyMouse()  # gv: use of pymouse module
        x, y = m.position()  # gv: gets mouse current position coordinates during click
        #print('position:', x, y)  #gv: just for debugging
        m.click(x, y, 2)  # gv: the third argument represents the mouse button click (1 left,2 right,3 middle)
        # GV: Right click is sent to wherever your mouse pointer is on the time of click.

def initiate_gesture_find():
    """
    This function will scan all input devices until it finds an
    ELAN touchscreen. It will then enter a loop to monitor this device
    without blocking its usage by the system.
    """
    for device in list_devices():
        dev = InputDevice(device)
        if (dev.name == 'ELAN Touchscreen') or (dev.name == 'Atmel Atmel maXTouch Digitizer'):
            break
    codes = dev.capabilities()
    Abs_events = {}
    for code in codes:
        if code == 3:
            for type_code in codes[code]:
                Abs_events[type_code[0]] = ecodes.ABS[type_code[0]]

    MT_event = None
    for event in dev.read_loop():
        if MT_event:
            if MT_event.discard == 1:
                MT_event = None
        if event.type == ecodes.EV_ABS:
            if MT_event is None:
                MT_event = TrackedEvent()
            event_code = Abs_events[event.code]
            if event_code == 'ABS_MT_SLOT':
                MT_event.add_finger(event.value)
            elif event_code == 'ABS_X' or event_code == 'ABS_Y':
                MT_event.position_event(event_code, event.value)
            elif event_code == 'ABS_MT_TRACKING_ID':
                if event.value == -1:
                    MT_event.remove_fingers()
                else:
                    MT_event.trackit()

if __name__ == '__main__':
    initiate_gesture_find()
