#!/usr/bin/env python

import numpy as np

class HumanControlDevice(object):
    """HumanControlDevice

    Gets positional and pointing vector information from the Phantom Omni
    6-DOF controller. This controller data is then used to control the
    robotic simulation enviroment of the Mitsubishi PA10 robotic arm.
    """
    def __init__(self):
        self._t = 0.0 # [s]
        self._dt = 0.01 # [s]

        self._prev_pos = np.array([0.0, 0.0, 0.0])
        self._cur_pos = np.array([0.0, 0.0, 0.0])

        self._cur_linear_vel = np.array([0.0, 0.0, 0.0])

        self._prev_angle = np.array([0.0, 0.0, 0.0])
        self._cur_angle = np.array([0.0, 0.0, 0.0])

        self._cur_angular_vel = np.array([0.0, 0.0, 0.0])

        return


    def set_dt(self, dt):
        self._dt = dt
        return


    def update(self):
        self._t += self._dt

        # Get the new tooltip position from the device
        self._prev_pos = self._cur_pos.copy()
        self._cur_pos = self._get_pos()

        # Calculate the change in linear velocity
        self._cur_linear_vel = (self._cur_pos - self._prev_pos) / self._dt

        # Get the new tooltip angle from the device
        self._prev_angle = self._cur_angle.copy()
        self._cur_angle = self._get_angle()

        self._cur_angular_vel = (self._cur_angle - self._prev_angle) / self._dt

        return


    def get_linear_vel(self):
        return self._cur_linear_vel


    def get_angular_vel(self):
        return self._cur_angular_vel


    def _get_pos(self):
        # TODO: Poll the Phantom Omni device for this information
        pos = self._oscillation_test()
        return pos


    def _get_angle(self):
        # TODO: Poll the Phantom Omni device for this information
        return np.array([0.0, 0.0, 0.0])


    def _oscillation_test(self):
        """Oscillation Test

        Returns a 3-dimensional array of sin values as a function of time.
        "amps" and "freqs" are 3-element adjustable parameters to control 
        the sinusoidal oscillations from the starting position.
        """
        a = np.array([0.15, 0.0, 0.15])
        f = np.array([1.0, 0.0, 0.5])
        y = a * np.sin(2.0 * np.pi * self._t * f)
        return y
