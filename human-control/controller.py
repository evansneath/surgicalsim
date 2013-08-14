#!/usr/bin/env python

import socket
import struct
import numpy as np
from multiprocessing import Process, Value

G_OMNI_MSG_FMT = '>bifffffff'

class PhantomOmniData(dict):
    """PhantomOmniData class

    Inherits dictionary class in order to provide an effective way to parse
    raw data sent from the Phantom Omni controller over TCP and store that
    data in an easy-to-use dictionary format.

    Inherits:
        dict: Standard library dictionary class.

    Methods:
        parse: Parses and stores raw data from a TCP transfer as a dictionary.
    """
    BUTTON_1 = 1
    BUTTON_2 = 2

    def __init__(self, raw_data=None):
        super(PhantomOmniData, self).__init__()

        self['docked'] = False
        self['button1'] = False
        self['button2'] = False
        self['position'] = np.array([0.0, 0.0, 0.0])
        self['angle'] = np.array([0.0, 0.0, 0.0])
        self['dt'] = 0.0

        if raw_data is not None:
            self.parse(raw_data)

        return


    def parse(self, raw_data):
        global G_OMNI_MSG_FMT

        unpacked_data = struct.unpack(G_OMNI_MSG_FMT, raw_data)

        self['docked'] = unpacked_data[0] == True
        self['button1'] = unpacked_data[1] & self.BUTTON_1
        self['button2'] = unpacked_data[1] & self.BUTTON_2
        self['position'] = np.array([
            unpacked_data[2],
            unpacked_data[3],
            unpacked_data[4]
        ]
        self['angle'] = np.array([
            unpacked_data[5],
            unpacked_data[6],
            unpacked_data[7]
        ]
        self['dt'] = unpacked_data[8]

        return


class HumanControlDevice(Process):
    """HumanControlDevice

    Gets positional and pointing vector information from the Phantom Omni
    6-DOF controller. This controller data is then used to control the
    robotic simulation enviroment of the Mitsubishi PA10 robotic arm.
    """
    def __init__(self, shared_data):
        """Initialization

        Initializes the superclass of multiprocess.Process and attributes
        necessary for determining position, rotation, and velocities.

        Arguments:
            shared_data: Stores the latest packet of data received by the
                Phantom Omni device.
        """
        global G_OMNI_MSG_FMT

        super(HumanControlDevice, self).__init__()

        self._OMNI_MSG_SIZ = struct.calcsize(G_OMNI_MSG_FMT)

        self._data = shared_data
        self._lock = multiprocessing.Lock()
        
        # Create the TCP socket to communicate to the controller
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # This holds the client socket object upon connection
        self._q = None

        self._t = 0.0 # [s]
        self._dt = 0.01 # [s]

        self._prev_pos = np.array([0.0, 0.0, 0.0])
        self._cur_pos = np.array([0.0, 0.0, 0.0])

        self._cur_linear_vel = np.array([0.0, 0.0, 0.0])

        self._prev_angle = np.array([0.0, 0.0, 0.0])
        self._cur_angle = np.array([0.0, 0.0, 0.0])

        self._cur_angular_vel = np.array([0.0, 0.0, 0.0])

        self._latest_data = None

        return


    def set_dt(self, dt):
        self._dt = dt
        return


    def run(self):
        while True:


        return
            

    def connect(self, ip, port):
        # Determine the ip and port of the controller to connect
        self._s.bind((ip, port))

        # Open the socket for one client
        self._s.listen(1)

        print '>>> Listening for Phantom Omni connection...'

        # Connect to the client socket
        (self._q, q_addr) = self._s.accept()

        print '>>> Connected to Phantom Omni at %s' % str(q_addr)

        return


    def disconnect(self):
        self._s.close()


    def _receive_data(self):
        raw_data = self._s.recv(self._OMNI_MSG_SIZ)
        data = PhantomOmniData(raw_data)
        return data


    def _update(self, data):
        # Get the new tooltip position from the device
        self._prev_pos = self._cur_pos.copy()
        self._cur_pos = data['position']

        # Calculate the change in linear velocity
        self._cur_linear_vel = (self._cur_pos - self._prev_pos) / self._dt

        # Get the new tooltip angle from the device
        self._prev_angle = self._cur_angle.copy()
        self._cur_angle = data['angle']

        self._cur_angular_vel = (self._cur_angle - self._prev_angle) / self._dt

        return


    def get_linear_vel(self):
        return self._cur_linear_vel


    def get_angular_vel(self):
        return self._cur_angular_vel


    def get_pos(self):
        return self._cur_pos


    def _get_angle(self):
        return self._cur_angle


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
