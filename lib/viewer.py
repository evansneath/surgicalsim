#!/usr/bin/env python

"""Viewer module

Contains classes to launch the OpenGL Surgical Sim viewer application.

Author:
    Evan Sneath - evansneath@gmail.com

License:
    Open Software License v3.0

Classes:
    ViewerInterface: Provides an interface for launching and communication with
        the OpenGL viewer application.
    Viewer: A customized viewer class for the Surgical Sim application.
"""

import inspect
import subprocess

from pybrain.rl.environments.ode.viewer import ODEViewer


class ViewerInterface(object):
    """ViewerInterface class

    Acts as the main method of launching and communicating with the Viewer
    class objects from a python parent program.

    Methods:
        start: Start the viewer process.
        update: Updates the interface with useful viewer information.
        stop: Terminate the viewer process.
    """
    def __init__(
            self, server_ip='127.0.0.1', viewer_ip='127.0.0.1',
            port='21590', buffer='16384', verbose=False):
        """Initialize

        Initializes the ViewerInterface class with all class attributes.

        Arguments:
            server_ip: The IP address of the server to recieve messages.
            viewer_ip: The IP address of the HumanControlViewer class.
            port: The port to carry out communication.
            buffer: The message buffer size.
            verbose: Determines if extra debug messages are printed.
        """
        super(ViewerInterface, self).__init__()

        # Define an attribute to hold the spawned Viewer processs
        self._process = None

        return

    def update(self):
        """Update Viewer Interface

        Updates the interface with useful information about the viewer
        status and control signals passed back from the viewer.
        """
        # Poll the process. This updates the return code
        self._process.poll()

        if self._process.returncode is None:
            # TODO: The process is dead. Let the main loop know
            pass

        return

    def start(self):
        """Start Viewer

        Starts a new instance of the viewer. Only one instance may exist
        at a time.
        """
        if self._process is None:
            # Detect the current file path of this module
            module_file_path = inspect.getfile(inspect.currentframe())

            # TODO: When the process is spawned, send over all arguments
            # passed into the interface object

            # Launch this own file's main function in a new process
            self._process = subprocess.Popen([module_file_path])

        return

    def stop(self):
        """Stop Viewer

        Terminates the viewer process if it was started.
        """
        if self._process is not None:
            # Kill the viewer process
            self._process.terminate()

        return


class Viewer(ODEViewer):
    """Viewer class

    A customized ODEViewer class for the Surgical Sim application.

    Inherits:
        ODEViewer: The PyBrain OpenGL-based viewer for the ODE engine.

    Attributes:
        paused: A boolean value to determine if the viewer is paused.
        stopped: A boolean value to determine if the viewer is stopped.
    """
    def __init__(
            self, server_ip='127.0.0.1', viewer_ip='127.0.0.1',
            port='21590', buffer='16384',
            verbose=False):
        """Initialization

        Initializes attributes for the base class of ODEViewer as well as new
        attributes defined for HumanControlViewer class.

        Arguments:
            server_ip: The IP address of the server to recieve messages.
            viewer_ip: The IP address of the HumanControlViewer class.
            port: The port to carry out communication.
            buffer: The message buffer size.
            verbose: Determines if extra debug messages are printed.
        """
        super(Viewer, self).__init__(
            servIP=server_ip,
            ownIP=viewer_ip,
            port=port,
            buf=buffer,
            verbose=verbose,
            window_name='Surgical-Sim'
        )

        self.paused = False
        self.stopped = False

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
    viewer = Viewer()
    viewer.start()
