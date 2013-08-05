#!/usr/bin/env python

import numpy as np


class HumanControlKinematics(object):
    """HumanControlKinematics class

    Given angles and velocities for joints of the PA10, the class
    calculates the appropriate torques to apply.
    """
    def __init__(self):
        super(HumanControlKinematics, self).__init__(self)
        return
