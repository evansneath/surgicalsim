#!/usr/bin/env python

import socket
import struct
import time

try:
    import AppKit
except ImportError as e:
    print ('AppKit module not found. Install XCode and run this ' +
           'program outside of virtual environments')
    raise e

try:
    import Quartz
except ImportError as e:
    print ('Quartz module not found. Install XCode and run this ' +
           'program outside of virtual environments')
    raise e

"""
NOTES:

    This program connects to a local (127.0.0.1:5555) TCP server and feeds
    current mouse data to the surgical-sim human control application.

    The method in which the mouse position is captured here
    is only compatible with OSX operating system bindings.

    AppKit is also required. This is an standard OSX python module.
    If import errors occur regarding AppKit, make sure the program
    is executed outside of virtual environments and that AppKit is
    available in the current python's site-packages directory.

    Because this program must be run outside of virtual environments,
    I removed all use of non-standard python libraries.

    The method for capturing mouse position in OSX was derived from
    the work of the PyUserInput module. The source code for this module
    can be found here: https://github.com/SavinaRoja/PyUserInput
"""

def main():
    # Use hardcoded TCP connection ip and port
    TCP_IP = '127.0.0.1'
    TCP_PORT = 5555

    # Define the message format and calculate the size. For details on this,
    # see human-control/controller.py
    MSG_FMT = '!iiddddddd'
    msg_siz = struct.calcsize(MSG_FMT)

    # Get the screen size information to normalize the mouse position
    screen_width = Quartz.CGDisplayPixelsWide(0)
    screen_height = Quartz.CGDisplayPixelsHigh(0)

    # Define the scaling factors for the cursor. Note that the cursor position
    # is normalized by screen height and screen width so that the x and y
    # outputs are limited between 0 and 1.

    # Limit the movement of the cursor to the environment table for now
    x_scale = 0.3
    y_scale = 1.0
    # Negate to flip the z axis in order to move relative to camera position
    z_scale = -0.3

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

    print '>>> Begin sending...'

    while True:
        t_start = time.time()

        # Get the most current mouse position. Normalized and scaled
        pos = get_mouse_pos(
            screen_width,
            screen_height,
            x_scale,
            y_scale,
            z_scale
        )

        msg = struct.pack(
            MSG_FMT,
            False,                  # docked
            0,                      # buttons
            pos[0], pos[1], pos[2], # positions
            0.0, 0.0, 0.0,          # angles
            dt                      # dt
        )

        try:
            s.send(msg)
        except socket.error as e:
            print '>>> Unable to send packet: %s' % (e.strerror)
            return

        t_send = time.time() - t_start

        # Sleep the difference of the time so we're only sending every dt seconds
        t_diff = dt - t_send

        if t_diff > 0.0:
            time.sleep(t_diff)
        else:
            # The calculation and sending took longer than our dt. We won't do
            # anything about this here, but it should be noted. Only worry
            # about this is the message shows up repetitively
            print '>>> Over RT threshold!'

        t += dt

    return


def get_mouse_pos(screen_width, screen_height, x_scale, y_scale, z_scale):
    """Get Mouse Position

    Gets the current mouse position on the OSX operating system. Requires
    objective-c to run. OSX Quartz and AppKit must be available modules.

    Arguments:
        screen_width: The width of the screen in pixels.
        screen_height: The height of the screen in pixels.
        x_scale: The value in meters to scale the normalized 'x' position.
        y_scale: Same as x_scale for the 'y' position.
        z_scale: Same and x_scale and y_scale for the 'z' position.

    Returns:
        3-item list containing the (x, y, z) positioning of the cursor.
    """
    # Define all starting positions. This is really only useful if the
    # axis is locked, otherwise these starting positions will be overwritten
    pos = [0.0, 0.1, 0.0]

    # Modify only the x and z positions. The y position is locked
    (pos[0], pos[2]) = AppKit.NSEvent.mouseLocation()

    # Scale/normalize
    pos[0] *= x_scale / screen_width
    pos[1] *= y_scale
    pos[2] *= z_scale / screen_height

    # Shift the range from (0.0, 1.0) to (0.5, 0.5)
    pos[0] -= x_scale / 2.0
    pos[2] -= z_scale / 2.0

    return pos


if __name__ == '__main__':
    main()
