#!/usr/bin/env python

"""Simulation module

Contains the simulation class. Simulation handles the main event loop of
the Surgical Sim PA10 neural network program.

Author:
    Evan Sneath - evansneath@gmail.com

License:
    Open Software License v3.0

Classes:
    NeuralSimulation: The main event loop manager for the simulation.
"""


# Import external modules
import os
import time
import cPickle
import numpy as np

# Import application modules
from world import NeuralSimWorld

# Import surgicalsim modules
from surgicalsim.lib.environment import EnvironmentInterface
from surgicalsim.lib.viewer import ViewerInterface


def oscillation_test(t, amp, freq):
    y = amp * np.cos(t * freq * 2.0 * np.pi)
    return y


class NeuralSimulation(object):
    """NeuralSimulation class

    Responsible for initialization of all children objects such as the
    Open Dynamics Engine environment and OpenGL viewer. Starts the main
    event loop with real-time constraints.

    Attributes:
        env: The Open Dynamics Engine environment.
        viewer: The OpenGL viewer for the ODE environment.

    Methods:
        start: Begins the main event loop.
    """
    env = None
    viewer = None

    def __init__(self, randomize=False, verbose=False):
        """Initialize

        Creates the environment and viewer objects required to run the neural
        network PA10 robotic arm simulation.

        Arguments:
            randomize: Determines if the test article gates will be randomized.
                (Default: False)
            verbose: Determines the level out debug output generated.
                (Default: False)
        """
        # Generate the XODE file
        XODE_FILENAME = 'model' # .xode is appended automatically

        print '>>> Generating world model'
        if os.path.exists('./'+XODE_FILENAME+'.xode'):
            os.remove('./'+XODE_FILENAME+'.xode')

        xode_model = NeuralSimWorld(
                name=XODE_FILENAME,
                randomize_test_article=randomize
        )
        xode_model.generate()

        # Start environment
        print '>>> Starting environment'
        self.env = EnvironmentInterface(
                xode_filename='./'+XODE_FILENAME+'.xode',
                realtime=False,
                verbose=verbose,
                gravity=0.0
        )

        # Start viewer
        print '>>> Starting viewer'
        self.viewer = ViewerInterface(verbose=verbose)
        self.viewer.start()

        return

    def start(self, fps=60, fast_step=False):
        """Start

        Begin the continuous event loop for the simulation. This event loop
        can be exited using the ctrl+c keyboard interrupt. Real-time
        constraints are enforced. [Hz]

        Arguments:
            fps: The value of frames per second of the simulation.
                (Default: 60 [Hz])
            fast_step: If True, the ODE fast step algorithm will be used.
                This is faster and requires less memory but is less accurate.
                (Default: False)
        """
        paused = False
        stopped = False

        # Define the simulation frame rate
        t = 0.0
        dt = 1.0 / float(fps) # [s]

        # Keep track of time overshoot in the case that simulation time must be
        # increased in order to maintain real-time constraints
        t_overshoot = 0.0

        while not stopped:
            t_start = time.time()

            # If the last calculation took too long, catch up
            dt_warped = dt + t_overshoot

            self.env.set_dt(dt_warped)

            # TODO: Update the viewer with the latest control signals
            #viewer.update()

            if paused:
                self.env.step(paused=True, fast=fast_step)
                continue

            # TODO: Sensing and actuation from neural network happens here

            # Rotational velocities must be inputted to ODE in rad/s
            #pa10_joint_vels = np.deg2rad(np.array([
            #    1.0, # S1 velocity [deg/s] (converted to rad/s later)
            #    1.0, # S2
            #    1.0, # S3
            #    1.0, # E1
            #    1.0, # E2
            #    1.0, # W1
            #    1.0, # W2
            #]))

            # Perform a simple oscillation test to test the joint position
            # accuracy
            amps = np.array([0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
            freq = 0.25
            pa10_joint_vels = oscillation_test(t, amps, freq)

            # Step through the world by 1 time frame and actuate pa10 joints
            self.env.performAction(pa10_joint_vels, fast=fast_step)
            t += dt_warped

            # Determine the difference in virtual vs actual time
            t_warped = dt - (time.time() - t_start)

            # Attempt to enforce real-time constraints
            if t_warped >= 0.0:
                # The calculation took less time than the virtual time. Sleep
                # the rest off
                time.sleep(t_warped)
                t_overshoot = 0.0
            else:
                # The calculation took more time than the virtual time. We need
                # to catch up with the virtual time on the next time step
                t_overshoot = -t_warped

        return

    def __del__(self):
        """Delete (del)

        Attempts to shut down any active engines and kills off spawned
        class objects.
        """
        # Kill the OpenGL viewer process
        if self.viewer is not None:
            self.viewer.stop()
            del self.viewer

        # Kill the ODE environment objects
        if self.env is not None:
            self.env.stop()
            del self.env

        return


if __name__ == '__main__':
    sim = NeuralSimulation()
    sim.start()
