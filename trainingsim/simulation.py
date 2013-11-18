#!/usr/bin/env python

"""Simulation module

Contains the simulation class. Simulation handles the main event loop of
the Surgical Sim training program.

Author:
    Evan Sneath - evansneath@gmail.com

License:
    Open Software License v3.0

Classes:
    TrainingSimulation: The main event loop manager for the simulation.
"""


# Import external modules
import os
import time
import numpy as np

# Import application modules
from world import TrainingSimWorld

# Import surgicalsim modules
from surgicalsim.lib.environment import EnvironmentInterface
from surgicalsim.lib.controller import PhantomOmniInterface
from surgicalsim.lib.viewer import ViewerInterface


class TrainingSimulation(object):
    """TrainingSimulation class

    Responsible for initialization of all children objects such as the
    Open Dynamics Engine environment, Phantom Omni controller, and OpenGL
    viewer. Starts the main event loop with real-time constraints.

    Attributes:
        env: The Open Dynamics Engine environment.
        omni: The Phantom Omni robotic controller connection.
        viewer: The OpenGL viewer for the ODE environment.
        saved_data: A list of tuples containing data from the simulation.

    Methods:
        start: Begins the main event loop.
    """
    env = None
    omni = None
    viewer = None
    saved_data = None

    gate_names = [
        'gate0',
        'gate1',
        'gate2',
        'gate3',
        'gate4',
        'gate5',
        'gate6',
        'gate7',
    ]

    def __init__(self, randomize=False, network=False, verbose=False):
        """Initialize

        Creates the environment, viewer, and (Phantom Omni) controller objects
        required to run the human data capture simulation.

        Arguments:
            randomize: Determines if the test article gates will be randomized.
                (Default: False)
            network: Determines if the omni connection is local or networked.
                (Default: False)
            verbose: Determines the level out debug output generated.
                (Default: False)
        """
        # Generate the XODE file
        XODE_FILENAME = 'model' # .xode is appended automatically

        print '>>> Generating world model'
        if os.path.exists('./'+XODE_FILENAME+'.xode'):
            os.remove('./'+XODE_FILENAME+'.xode')

        xode_model = TrainingSimWorld(
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

        # Set up all grouped bodies in the environment
        self.env.groups = {
            'pointer': ['tooltip', 'stick'],
        }

        # Start viewer
        print '>>> Starting viewer'
        self.viewer = ViewerInterface(verbose=verbose)
        self.viewer.start()

        # Start controller
        print '>>> Starting Phantom Omni interface'
        self.omni = PhantomOmniInterface()

        if network:
            ip = raw_input('<<< Enter host ip: ')
            port = int(raw_input('<<< Enter tcp port: '))
        else:
            ip = '127.0.0.1'
            port = 5555

        # Try to connect to the Phantom Omni controller
        self.omni.connect(ip, port)

        self.saved_data = np.array([])

        return

    def start(self, fps=60):
        """Start

        Begin the continuous event loop for the simulation. This event loop
        can be exited using the ctrl+c keyboard interrupt. Real-time
        constraints are enforced.

        Arguments:
            fps: The value of frames per second of the simulation.
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
            self.omni.set_dt(dt_warped)

            # TODO: Update the viewer with the latest control signals
            #viewer.update()

            if paused:
                self.env.step(paused=True)
                continue

            # Populate the controller with the most up-to-date data
            self.omni.update()

            # Determine the input data to record
            sample_input = np.array([
                t,
            ]).flatten()

            # Capture the gate position at each time step
            for gate_name in self.gate_names:
                gate_pos = np.array(self.env.get_body_pos(gate_name)).flatten()
                sample_input = np.concatenate((sample_input, gate_pos))

            # Determine the output data to record
            sample_output = np.array([
                self.env.get_body_pos('tooltip'),
                #self.omni.get_angle(),
            ]).flatten()

            # Join the sample input/output
            data_sample = np.concatenate((sample_input, sample_output), axis=0)

            # Save the data
            self.save_data(data_sample)

            # Get the updated linear/angular velocities of the tooltip
            linear_vel = self.omni.get_linear_vel()
            angular_vel = self.omni.get_angular_vel()

            # Set the linear and angular velocities of the simulation
            self.env.set_group_linear_vel('pointer', linear_vel)
            self.env.set_group_angular_vel('pointer', angular_vel)

            # Step through the world by 1 time frame
            self.env.step()

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


    def save_data(self, data_sample):
        """Save Data

        Saves a sample of data into the simulation's saved data array.

        Arguments:
            data_sample: A sample of input/output data from a single time step.
        """
        if len(self.saved_data):
            self.saved_data = np.vstack((self.saved_data, data_sample))
        else:
            self.saved_data = np.concatenate((self.saved_data, data_sample))

        return


    def __del__(self):
        """Delete (del)

        Attempts to shut down any active engines and kills off spawned
        class objects.
        """
        print self.saved_data

        # Kill the OpenGL viewer process
        if self.viewer is not None:
            self.viewer.stop()
            del self.viewer

        # Kill the ODE environment objects
        if self.env is not None:
            self.env.stop()
            del self.env

        # Kill the Phantom Omni controller process
        if self.omni is not None:
            self.omni.disconnect()
            del self.omni

        return


if __name__ == '__main__':
    sim = TrainingSimulation()
    sim.start()
