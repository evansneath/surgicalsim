#!/usr/bin/env python

import array
import time
import socket
import struct
import numpy as np
import multiprocessing

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

        # Unpack the byte data with struct module
        unpacked_data = struct.unpack(G_OMNI_MSG_FMT, raw_data)

        # Load all of the unpacked data into dictionary items for easy lookup
        self['docked'] = unpacked_data[0] == True
        self['button1'] = unpacked_data[1] & self.BUTTON_1
        self['button2'] = unpacked_data[1] & self.BUTTON_2
        self['position'] = np.array([
            unpacked_data[2],
            unpacked_data[3],
            unpacked_data[4]
        ])
        self['angle'] = np.array([
            unpacked_data[5],
            unpacked_data[6],
            unpacked_data[7]
        ])
        self['dt'] = unpacked_data[8]

        return


class PhantomOmniInterface(object):
    """HumanControlDevice

    Gets positional and pointing vector information from the Phantom Omni
    6-DOF controller. This controller data is then used to control the
    robotic simulation enviroment of the Mitsubishi PA10 robotic arm.
    """
    def __init__(self, dt=0.01):
        super(PhantomOmniInterface, self).__init__()

        # Create a shared array of the length of one message. This will be
        # used to store the most current data from the Phantom Omni controller
        data_len = struct.calcsize(G_OMNI_MSG_FMT)

        # NOTE: Type 'b' = byte (actually signed char). data_len = array size
        self._cur_data = multiprocessing.Array('b', data_len, lock=True)
        self._is_connected = multiprocessing.Value('b', False)

        # Create an instance of a Phantom Omni thread. This will act as a
        # separate process which always stores the latest information from the
        # Phantom Omni device
        self._thread = None

        # Initialize time and difference in time between polling. dt is used
        # only in calculations to determine linear/angular velocities
        self._t = 0.0 # [s]
        self._dt = dt # [s]

        # Create arrays to hold positional/rotational values and their
        # respective velocities. Initialize to zeros
        self._prev_pos = np.array([0.0, 0.0, 0.0])
        self._cur_pos = np.array([0.0, 0.0, 0.0])

        self._cur_linear_vel = np.array([0.0, 0.0, 0.0])

        self._prev_angle = np.array([0.0, 0.0, 0.0])
        self._cur_angle = np.array([0.0, 0.0, 0.0])

        self._cur_angular_vel = np.array([0.0, 0.0, 0.0])
        return


    def set_dt(self, dt):
        """Set dt

        Sets the delta-time variable. This is used for varying dt for use in
        real-time systems.

        Attributes:
            dt: The difference in time between this and the last update.
        """
        self._dt = dt
        return


    def connect(self, ip, port):
        """Connect to TCP Client

        Attempts a connection to an incoming client TCP socket.

        Attributes:
            ip: The ip address of the incoming connection as a string.
            port: The port of the incoming connection as a int.
        """
        # Populate the thread object, hand over the connected socket
        self._thread = PhantomOmniThread(
            ip,
            port,
            self._is_connected,
            self._cur_data
        )

        # Start the Phantom Omni thread. The thread will continue until the
        # interface is killed. Latest gathered data from the thread will be
        # found in the _cur_data shared value object
        self._thread.start()

        # Wait around until the thread has successfully connected
        while not self._is_connected.value:
            time.sleep(0.01)

        return


    def disconnect(self):
        """Disconnect from TCP Client

        Attempts to disconnect the TCP server from the incoming client.
        """
        # Terminate the data collection thread
        self._thread.terminate()

        return


    def update(self):
        """Update Values

        Gets the latest Phantom Omni data from the messaging thread. The
        method updates each positional, rotational, and velocity array with
        appropriate calculations.
        """
        # Convert shared data array into a byte list form
        raw_data = array.array('b', list(self._cur_data)).tostring()

        # Grab the newest Omni data from the shared thread array
        parsed_data = PhantomOmniData(raw_data=raw_data)

        # Get the new tooltip position from the device
        self._prev_pos = self._cur_pos.copy()
        self._cur_pos = parsed_data['position']

        # Calculate the change in linear velocity
        self._cur_linear_vel = (self._cur_pos - self._prev_pos) / self._dt

        # Get the new tooltip angle from the device
        self._prev_angle = self._cur_angle.copy()
        self._cur_angle = parsed_data['angle']

        self._cur_angular_vel = (self._cur_angle - self._prev_angle) / self._dt

        return


    def get_linear_vel(self):
        """Get Linear Velocity

        Returns the current linear velocity of the Phantom Omni controller
        in meters per second.

        Returns:
            1x3 numpy array of (x, y, z) velocities in m/s.
        """
        return self._cur_linear_vel


    def get_angular_vel(self):
        """Get Angular Velocity

        Returns the current angular velocity of the Phantom Omni controller
        in radians per second.

        Returns:
            1x3 numpy array of (x, y, z) angular velocities in rad/s.
        """
        return self._cur_angular_vel


    def get_pos(self):
        """Get Position

        Returns the current position of the Phantom Omni controller in meters.

        Returns:
            1x3 numpy array of (x, y, z) positions in m.
        """
        return self._cur_pos


    def _get_angle(self):
        """Get Angle

        Returns the current angle of the Phantom Omni controller in radians.

        Returns:
            1x3 numpy array of (x, y, z) angles in rad.
        """
        return self._cur_angle


class PhantomOmniThread(multiprocessing.Process):
    def __init__(self, tcp_ip, tcp_port, is_connected, shared_array):
        """Initialization

        Initializes the superclass of multiprocess.Process and attributes
        necessary for determining position, rotation, and velocities.

        Arguments:
            tcp_ip: The ip address of the client connection.
            tcp_port: The port of the client connection.
            shared_array: Stores the latest packet of data received by the
                Phantom Omni device. This is raw byte data format.
        """
        super(PhantomOmniThread, self).__init__()

        # Populate the TCP ip and port attributes
        self._ip = tcp_ip
        self._port = tcp_port

        # Create the TCP socket to communicate to the controller
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # This holds the client socket object upon connection
        self._q = None

        # Store the shared array to populate with the latest data
        self._data = shared_array

        # Calculate the size of the array so we don't have to do this more
        # than once
        self._data_size = len(self._data)

        self._is_connected = is_connected
        
        return


    def run(self):
        """Run (Subclassed)

        A subclassed function from multiprocessing.Process class. This method
        is called when the multiprocess.Process.start() method is invoked.
        This particular implementation is an infinite loop which gathers TCP
        incoming messages.
        """
        # Set the server socket to listen to the given ip and port
        self._s.bind((self._ip, self._port))

        # Open the socket for one client
        self._s.listen(1)

        print '>>> Listening for Phantom Omni connection...'

        # Connect to the client socket
        (self._q, q_addr) = self._s.accept()
        self._is_connected.value = True

        print '>>> Connected to Phantom Omni at %s:%d' % q_addr

        while True:
            # Get newest data until this process is terminated
            incoming = self._q.recv(self._data_size)

            for index, byte in enumerate(incoming):
                self._data[index] = ord(byte)

        return
