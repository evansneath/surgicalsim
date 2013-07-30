#!/usr/bin/env python

import sys
from pybrain.rl.environments.ode.viewer import ODEViewer


class HumanCaptureViewer(ODEViewer):
    """HumanCaptureViewer class

    Inherits ODEViewer in order to create an acceptable environment to capture
    human movement data during the controlled robotic simulation.
    """
    def __init__(self, server_ip='127.0.0.1', viewer_ip='127.0.0.1', port='21590', buffer='16384'):
        """Init

        Initializes attributes for the base class of ODEViewer as well as new
        attributes defined for HumanCaptureViewer class.

        Attributes:
            server_ip: The IP address of the server to recieve messages.
            viewer_ip: The IP address of the HumanCaptureViewer class.
            port: The port to carry out communication.
            buffer: The message buffer size.
        """
        # Call the ODEViewer init function, begin listening over UDP
        super(HumanCaptureViewer, self).__init__(server_ip, viewer_ip, port, buffer)

        # Hold attributes specific to the HumanCaptureViewer
        self.pause = False

        return


    def _keyfunc(self, c, x, y):
        """OpenGL Key Handler Function

        The '_keyfunc' function in ODEViewer is the handler function for
        OpenGL keystroke capturing. By overwriting this function, the actions
        of captured keystrokes are modified for this specific viewer.

        Arguments:
            c: The keystroke input.
            x: Unused (required for handler function).
            y: Unused (required for handler function).
        """
        if c == ' ':
            # If 'space' key is hit, pause the simulation
            self.pause = not self.pause
            print 'PAUSE' if self.pause else 'RESUME'
        elif c == 'q':
            # If 'q' key is hit, exit the viewer
            sys.exit()

        return


if __name__ == '__main__':
    args = sys.argv[1:]
    capture_viewer = HumanCaptureViewer(*args)
    capture_viewer.start()
