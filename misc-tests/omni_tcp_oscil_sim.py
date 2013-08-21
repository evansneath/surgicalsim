#!/usr/bin/env python

import numpy as np
import socket
import struct
import time


def main():
    # Use hardcoded TCP connection ip and port
    TCP_IP = '127.0.0.1'
    TCP_PORT = 5555

    # Define the message format and calculate the size
    MSG_FMT = '!iiddddddd'
    msg_siz = struct.calcsize(MSG_FMT)

    # Attempt to connect to the TCP server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((TCP_IP, TCP_PORT))
    except socket.error as e:
        print '>>> Unable to connect to server: %s' % (e.strerror)
        return

    # Keep track of the current time
    t = 0.0

    # Output 500 times per second
    dt = 1.0 / 500.0

    times = []

    print '>>> Begin sending...'

    while True:
        t_start = time.time()

        # Get the time-dependent position of the cursor. This is a sinusoidal
        # function of time
        pos = calc_oscillation(t)

        # Package the position for sending over TCP. Gimble angles are locked
        msg = struct.pack(
            MSG_FMT,
            False,                  # docked
            0,                      # buttons
            pos[0], pos[1], pos[2], # positions
            0.0, 0.0, 0.0,          # angles
            dt                      # dt
        )

        # Attempt to send a TCP packet
        try:
            s.send(msg)
        except socket.error as e:
            print '>>> Unable to send packet: %s' % (e.strerror)
            return

        t_send = time.time() - t_start

        # Sleep the difference of the time so we're only sending every dt seconds
        t_diff = dt - t_send

        if t_diff > 0.0:
            # Sleep to maintain the sending rate
            time.sleep(t_diff)
        else:
            # Real-time constraints are not being met. This simply means that the
            # processing and sending are greater than the set 'dt' value. This does
            # not necessarily mean that the server is receiving old/faulty data
            print '>>> Over RT threshold!'

        t += dt

    return


def calc_oscillation(t):
    """Calculate Oscillation

    Given a time in seconds, the position of the cursor is given with
    amplitude and frequency hardcoded for each x, y, and z positions.

    Arguments:
        t: The time to calculate the oscillations in seconds.

    Returns:
        A 3-dimensional numpy array with (x, y, z) cursor positions.
    """
    # To modify amplitude and frequency, modify these parameters
    amp = np.array([0.15, 0.0, 0.15])
    freq = np.array([1.0, 0.0, 2.0])

    return amp * np.sin(2.0 * np.pi * freq * t)


if __name__ == '__main__':
    main()
