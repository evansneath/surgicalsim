#!/usr/bin/env python

import sys
import subprocess

from pybrain.rl.environments.ode.viewer import ODEViewer


class ViewerInterface(object):
    """ViewerInterface class

    Acts as the main method of launching and communicating with the Viewer
    class objects from a python parent program.

    Methods:
        start: Start the viewer process.
        stop: Terminate the viewer process.
    """
    def __init__(self, server_ip='127.0.0.1', viewer_ip='127.0.0.1',
            port='21590', buffer='16384'):
        """Initialize

        Initializes the ViewerInterface class with all class attributes.
        """
        super(ViewerInterface, self).__init__()

        self._process = None

        return


    def start(self):
        """Start Viewer

        Starts a new instance of the viewer. Only one instance may exist
        at a time.
        """
        if self._process is None:
            # Launch this own file's main function in a new process
            self._process = subprocess.Popen(['./viewer.py'])

        return
    

    def stop(self):
        """Stop Viewer

        Terminates the viewer process if it was started.
        """
        if self._process is not None:
            # Kill the spawned process
            self._process.terminate()

        return


class Viewer(ODEViewer):
    def __init__(self, server_ip='127.0.0.1', viewer_ip='127.0.0.1',
            port='21590', buffer='16384', verbose=False):
        """Initialization

        Initializes attributes for the base class of ODEViewer as well as new
        attributes defined for HumanControlViewer class.

        Attributes:
            paused_obj: The shared value object to determine if the viewer is
                paused.
            stopped_obj: The shared value object to determine if the viewer is
                stopped.
            server_ip: The IP address of the server to recieve messages.
            viewer_ip: The IP address of the HumanControlViewer class.
            port: The port to carry out communication.
            buffer: The message buffer size.
        """
        super(Viewer, self).__init__(
            servIP=server_ip,
            ownIP=viewer_ip,
            port=port,
            buf=buffer,
            verbose=verbose
        )

        return


    def _keyboard_callback(self, key, x, y):
        """OpenGL Key Handler Function

        The '_keyfunc' function in ODEViewer is the handler function for
        OpenGL keystroke capturing. By overwriting this function, the actions
        of captured keystrokes are modified for this specific viewer.

        Arguments:
            c: The keystroke input.
            x: Unused (required for handler function).
            y: Unused (required for handler function).
        """
        # Call the superclass keyboard callback first. All of this
        # functionality is maintained
        super(Viewer, self)._keyboard_callback(key, x, y)

        # Add additional keyboard functionality
        if key == ' ':
            # If 'space' key is hit, pause the simulation
            self.paused = not self.paused
            print 'Pause' if self.paused else 'Resume'
        elif key == 'q':
            # If 'q' key is hit, exit the viewer
            self.stopped = True
            print 'Stop'

        return


if __name__ == '__main__':
    # Simple usage example
    viewer = Viewer()
    viewer.start()
