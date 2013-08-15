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
    MSG_FMT = '>bifffffff'
    msg_siz = struct.calcsize(MSG_FMT)

    # Attempt to connect to the TCP server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))

    # Keep track of the current time
    t = 0.0

    # Output 500 times per second
    dt = 1.0 / 500.0

    times = []

    print 'Begin sending...'

    while True:
        t_start = time.time()

        # Package 
        pos = calc_oscillation(t)

        msg = struct.pack(
            MSG_FMT,
            False,                  # docked
            0,                      # buttons
            pos[0], pos[1], pos[2], # positions
            0.0, 0.0, 0.0,          # angles
            dt                      # dt
        )

        s.send(msg)

        t_send = time.time() - t_start

        # Sleep the difference of the time so we're only sending every dt seconds
        time.sleep(dt - t_send)
        t += dt

    return


def calc_oscillation(t):
    amp = np.array([0.15, 0.0, 0.15])
    freq = np.array([1.0, 0.0, 2.0])
    y = amp * np.sin(2.0 * np.pi * freq * t)
    return y


if __name__ == '__main__':
    main()
