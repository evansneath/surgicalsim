#!/usr/bin/env python

class HumanControlDevice(object):
    """HumanControlDevice

    Gets positional and pointing vector information from the Phantom Omni
    6-DOF controller. This controller data is then used to control the
    robotic simulation enviroment of the Mitsubishi PA10 robotic arm.
    """
    def __init__(self):
        return


    def set_position(self, x, y, z):
        return


    def set_rotation(self, u, v, w):
        return


    def get_position(self):
        x, y, z = (None, None, None)
        return x, y, z


    def get_rotation(self):
        u, v, w = (None, None, None)
        return u, v, w
