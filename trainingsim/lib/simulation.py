#!/usr/bin/env python

"""Simulation module

Contains the simulation class. Simulation handles the main event loop of
the Surgical Sim training program.

Author:
    Evan Sneath - evansneath@gmail.com

License:
    Open Software License v3.0

Classes:
    Simulation: The main event loop manager for the simulation.
"""


# Import external modules
import os
import time
import cPickle

# Import application modules
from model import TrainingSimModel
from environment import TrainingSimEnvironment
from controller import PhantomOmniInterface
from viewer import ViewerInterface


class Simulation(object):
    """Simulation class

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

        xode_model = TrainingSimModel(
                name=XODE_FILENAME,
                randomize_test_article=randomize
        )
        xode_model.generate()

        # Start environment
        print '>>> Starting environment'
        self.env = TrainingSimEnvironment(
                xode_filename='./'+XODE_FILENAME+'.xode',
                realtime=False,
                verbose=verbose,
                gravity=0.0
        )

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

        # Initialize the tooltip data list
        self.saved_data = []

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

            # Record the positional and angular tooltip data
            data_pack = (self.omni.get_pos().tolist(),
                         self.omni.get_angle().tolist())
            self.saved_data.append(data_pack)

            # Get the updated linear/angular velocities of the tooltip
            linear_vel = self.omni.get_linear_vel()
            angular_vel = self.omni.get_angular_vel()

            # Set the linear and angular velocities of the simulation
            self.env.set_group_linear_vel('pointer', linear_vel)
            self.env.set_group_angular_vel('pointer', angular_vel)

            # Step through the world by 1 time frame
            self.env.step()

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

    def write_data(self, outfile):
        """Write Data

        Writes all data written to the saved_data list into the specified
        output file in a pickled format.

        Arguments:
            outfile: The relative or absolute path of the file to output the
                pickled simulation data.
        """
        with open(outfile, 'w+') as f:
            cPickle.dump(self.saved_data, f)

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

        # Kill the Phantom Omni controller process
        if self.omni is not None:
            self.omni.disconnect()
            del self.omni

        return


if __name__ == '__main__':
    sim = Simulation()
    sim.start()
