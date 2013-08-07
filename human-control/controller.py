#!/usr/bin/env python

import numpy as np

class HumanControlDevice(object):
    """HumanControlDevice

    Gets positional and pointing vector information from the Phantom Omni
    6-DOF controller. This controller data is then used to control the
    robotic simulation enviroment of the Mitsubishi PA10 robotic arm.
    """
    def __init__(self):
        self._pos = np.array([0.0, 0.0, 0.0])
        return


    def set_pos(self, pos):
        self._pos = np.array(pos)
        return


    def get_pos(self):
        return self._pos
