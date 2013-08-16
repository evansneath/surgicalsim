#!/usr/bin/env python

import sys
import multiprocessing
from pybrain.rl.environments.ode.viewer import ODEViewer


class ViewerInterface(object):
    def __init__(self, server_ip='127.0.0.1', viewer_ip='127.0.0.1',
            port='21590', buffer='16384'):
        super(ViewerInterface, self).__init__()

        self._stopped_obj = multiprocessing.Value('b', False)
        self._paused_obj = multiprocessing.Value('b', False)

        # Create the thread object to begin the viewer
        self._thread = ViewerThread(
            paused_obj=self._paused_obj,
            stopped_obj=self._stopped_obj,
            server_ip=server_ip,
            viewer_ip=viewer_ip,
            port=port,
            buffer=buffer
        )

        return


    def start(self):
        self._thread.start()
        return


    @property
    def is_paused(self):
        return self._paused_obj.value


    @property
    def is_stopped(self):
        return self._stopped_obj.value


class ViewerThread(multiprocessing.Process):
    """HumanControlViewer class

    Methods:
        start: Starts the viewer.
    """
    def __init__(self, paused_obj=None, stopped_obj=None, server_ip='127.0.0.1',
            viewer_ip='127.0.0.1', port='21590', buffer='16384'):
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
        super(ViewerThread, self).__init__()

        # Call the ODEViewer init function, begin listening over UDP
        self._viewer = Viewer(
            paused_obj=paused_obj,
            stopped_obj=stopped_obj,
            server_ip=server_ip,
            viewer_ip=viewer_ip,
            port=port,
            buffer=buffer,
            verbose=False
        )

        return


    def run(self):
        self._viewer.start()
        return


class Viewer(ODEViewer):
    def __init__(self, paused_obj=None, stopped_obj=None, server_ip='127.0.0.1',
            viewer_ip='127.0.0.1', port='21590', buffer='16384', verbose=False):
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
            server_ip,
            viewer_ip,
            port,
            buffer,
            verbose
        )

        # Hold shared value attributes for pausing and stopping the simulation
        self._paused_obj = paused_obj
        self._stopped_obj = stopped_obj

        if self._paused_obj is not None:
            self._paused_obj.value = False

        if self._stopped_obj is not None:
            self._stopped_obj.value = False

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
        if c == ' ' and self._paused_obj is not None:
            # If 'space' key is hit, pause the simulation
            self.paused = not self.paused
            print 'PAUSE' if self.paused else 'RESUME'
        elif c == 'q' and self._stopped_obj is not None:
            # If 'q' key is hit, exit the viewer
            self.stopped = True
            print 'STOP'

        return


if __name__ == '__main__':
    # Simple usage example
    viewer = Viewer()
    viewer.start()
