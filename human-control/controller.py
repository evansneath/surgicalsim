#!/usr/bin/env python

import sys
import threading

"""
This method of polling the keyboard via threads came from:
http://mail.python.org/pipermail/tutor/2001-November/009936.html
"""

data_ready = threading.Event()

class HumanControlDevice(threading.Thread):
    """HumanControlDevice

    Gets positional and pointing vector information from the Phantom Omni
    6-DOF controller. This controller data is then used to control the
    robotic simulation enviroment of the Mitsubishi PA10 robotic arm.
    """
    pos = [0.0, 0.0, 0.0]
    rot = [0.0, 0.0, 0.0]

    dx = 0.01
    dy = 0.01

    def run(self):
        char = sys.stdin.read(1)

        if char == 'd':
            self.pos[0] += self.dx
        elif char == 'a':
            self.pos[0] -= self.dx
        elif char == 'w':
            self.pos[1] += self.dy
        elif char == 's':
            self.pos[1] -= self.dy
        
        data_ready.set()

        return


    def get_pos(self):
        return self.pos
