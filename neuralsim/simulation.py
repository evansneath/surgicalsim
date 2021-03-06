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

import numpy as np

# Import application modules
from world import NeuralSimWorld

# Import surgicalsim modules
from surgicalsim.lib.environment import EnvironmentInterface
from surgicalsim.lib.viewer import ViewerInterface
from surgicalsim.lib.kinematics import PA10Kinematics

import surgicalsim.lib.network as network
import surgicalsim.lib.pathutils as pathutils
import surgicalsim.lib.constants as constants
import surgicalsim.lib.datastore as datastore


def oscillation(t, amp, freq):
    y = amp * np.sin(t * freq * 2.0 * np.pi)
    return y

def shaker_table(t, table_pos):
    amplitude = constants.G_TABLE_OSCILLATION_AMP
    frequency = constants.G_TABLE_OSCILLATION_FREQ

    new_y = oscillation(t, amplitude, frequency)
    new_pos = table_pos + np.array([0.0, new_y, 0.0])

    return new_pos


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
    rnn = None
    kinematics = None

    def __init__(self, randomize=False, rnn_xml=None, verbose=False):
        """Initialize

        Creates the environment and viewer objects required to run the neural
        network PA10 robotic arm simulation.

        Arguments:
            randomize: Determines if the test article gates will be randomized.
                (Default: False)
            rnn_xml: A XML filename containing neural network parameters. If
                None, a new neural network will be trained until convergence.
                (Default: None)
            verbose: Determines the level out debug output generated.
                (Default: False)
        """
        # Generate the XODE file
        XODE_FILENAME = 'model' # .xode is appended automatically

        print('>>> Generating world model')
        if os.path.exists('./'+XODE_FILENAME+'.xode'):
            os.remove('./'+XODE_FILENAME+'.xode')

        xode_model = NeuralSimWorld(
                name=XODE_FILENAME,
                randomize_test_article=randomize
        )
        xode_model.generate()

        print('>>> Generating RNN')

        # Determine if we need to train the neural network
        if rnn_xml is not None:
            print('>>> Loading RNN from file')
            self.rnn = network.PathPlanningNetwork()
            self.rnn.load_network_from_file(rnn_xml)
        else:
            print('>>> Training new RNN')
            self.rnn = network.train_path_planning_network()
            self.rnn.save_network_to_file(constants.G_RNN_XML_OUT)

        print('>>> Starting kinematics engine')
        self.kinematics = PA10Kinematics()

        # Start environment
        print('>>> Starting environment')
        self.env = EnvironmentInterface(
                xode_filename='./'+XODE_FILENAME+'.xode',
                realtime=False,
                verbose=verbose,
                gravity=constants.G_ENVIRONMENT_GRAVITY
        )

        # Start viewer
        print('>>> Starting viewer')
        self.viewer = ViewerInterface(verbose=verbose)
        self.viewer.start()

        # Set up all grouped bodies in the environment
        self.env.groups = {
            'pointer': ['tooltip', 'stick'],
        }

        return

    def start(self, fps, fast_step=False):
        """Start

        Begin the continuous event loop for the simulation. This event loop
        can be exited using the ctrl+c keyboard interrupt. Real-time
        constraints are enforced. [Hz]

        Arguments:
            fps: The value of frames per second of the simulation.
            fast_step: If True, the ODE fast step algorithm will be used.
                This is faster and requires less memory but is less accurate.
                (Default: False)
        """
        paused = False
        stopped = False

        # Define the total time for the tooltip traversal
        t_total = 20.0

        # Define the simulation frame rate
        t = 0.0 # [s]
        dt = 1.0 / float(fps) # [s]

        # Keep track of time overshoot in the case that simulation time must be
        # increased in order to maintain real-time constraints
        t_overshoot = 0.0

        # Get the initial path position (center of gate7)
        pos_start = self.env.get_body_pos('gate7') # [m]

        # Get the first position of the PA10 at rest
        pos_init = self.env.get_body_pos('tooltip') # [m]

        # Calculate the new required joint angles of the PA10
        #pa10_joint_angles = self.kinematics.calc_inverse_kinematics(pos_init, pos_start)

        # TODO: Move the PA10 end-effector to the starting position along the path

        # TODO: TEMP - Move the temporary end-effector pointer to the starting position
        self.env.set_group_pos('pointer', pos_start)

        # Generate long-term path from initial position
        t_input = np.linspace(start=0.0, stop=1.0, num=t_total/dt)
        t_input = np.reshape(t_input, (len(t_input), 1))

        rnn_path = self.rnn.extrapolate(t_input, [pos_start], len(t_input)-1)

        # Add the initial condition point back onto the data
        rnn_path = np.vstack((pos_start, rnn_path))

        # Retrieve one set of standard gate position/orientation data
        file_path = pathutils.list_data_files(constants.G_TRAINING_DATA_DIR)[0]

        gate_data = datastore.retrieve(file_path)

        gate_start_idx = constants.G_GATE_IDX
        gate_end_idx = gate_start_idx + constants.G_NUM_GATE_INPUTS

        # Reshape the gate positions data
        gate_data = gate_data[0:1,gate_start_idx:gate_end_idx]
        gate_data = np.tile(gate_data, (len(rnn_path), 1))

        # Complete the rnn path data
        rnn_path = np.hstack((t_input, gate_data, rnn_path))

        # Save generated path for later examination
        datastore.store(rnn_path, constants.G_RNN_STATIC_PATH_OUT)

        # Define a variable to hold the final path (with real-time correction)
        final_path = rnn_path[:-1].copy()
        path_saved = False

        # Detect all path segments between gates in the generated path
        segments = pathutils._detect_segments(rnn_path)

        path_idx = 0

        x_path_offset = np.array([0.0, 0.0, 0.0]) # [m]
        v_curr = np.array([0.0, 0.0, 0.0]) # [m/s]
        a_max = constants.G_MAX_ACCEL # [m/s^2]

        # Get the static table position
        x_table = self.env.get_body_pos('table')

        while not stopped:
            t_start = time.time()

            # If the last calculation took too long, catch up
            dt_warped = dt + t_overshoot

            self.env.set_dt(dt_warped)

            # Determine if the viewer is stopped. Then we can quit
            if self.viewer.is_dead:
                break

            # Pause the simulation if we are at the end
            if path_idx == len(rnn_path) - 1 or paused:
                self.env.step(paused=True, fast=fast_step)

                # If we have really hit the end of the simulation, save/plot the path
                if not paused and not path_saved:
                    # Save the final data to a file
                    datastore.store(final_path, constants.G_RNN_DYNAMIC_PATH_OUT)
                    path_saved = True

                continue

            # Not a very elegant solution to pausing at the start, but it works
            if t <= 1000.0:
                self.env.step(paused=True, fast=fast_step)
                t += dt_warped
                continue

            # Determine the current path segment
            curr_segment_idx = 0

            for segment_idx, segment_end in enumerate(segments):
                if path_idx <= segment_end:
                    curr_segment_idx = segment_idx
                    break

            x_curr = pathutils.get_path_tooltip_pos(rnn_path, path_idx) + x_path_offset
            x_next = pathutils.get_path_tooltip_pos(rnn_path, path_idx+1) + x_path_offset

            # Get the expected gate position
            x_gate_expected = pathutils.get_path_gate_pos(
                    rnn_path,
                    segments[curr_segment_idx],
                    curr_segment_idx
            )

            # Get the actual gate position
            x_gate_actual = self.env.get_body_pos('gate%d'%curr_segment_idx)

            # Calculate the new position from change to new gate position
            dx_gate = x_gate_actual - (x_gate_expected + x_path_offset)
            x_new = x_next + dx_gate

            # Calculate the new velocity
            v_new = (x_new - x_curr) / dt_warped

            # Calculate the new acceleration
            a_new = (v_new - v_curr) / dt_warped

            # Calculate the acceleration vector norm
            a_new_norm = np.linalg.norm(a_new)

            # Limit the norm vector
            a_new_norm_clipped = np.clip(a_new_norm, -a_max, a_max)

            # Determine the ratio of the clipped norm, protect against divide by zero
            if a_new_norm != 0.0:
                ratio_unclipped = a_new_norm_clipped / a_new_norm
            else:
                ratio_unclipped = 0.0

            # Scale the acceleration vector by this ratio
            a_new = a_new * ratio_unclipped

            # Calculate the new change in velocity
            dv_new = a_new * dt_warped
            v_new = v_curr + dv_new

            # Calculate the new change in position
            dx_new = v_new * dt_warped
            x_new = x_curr + dx_new

            # Modify final path data with current tooltip and gate positions
            pathutils.set_path_time(final_path, path_idx, t)
            pathutils.set_path_tooltip_pos(final_path, path_idx, x_curr)

            for gate_idx in range(constants.G_NUM_GATES):
                gate_name = 'gate%d' % gate_idx
                x_gate = self.env.get_body_pos(gate_name)
                pathutils.set_path_gate_pos(final_path, path_idx, gate_idx, x_gate)

            # Store this velocity for the next time step
            v_curr = v_new

            # Recalculate the current offset
            x_path_offset += x_new - x_next

            # Perform inverse kinematics to get joint angles
            pa10_joint_angles = self.kinematics.calc_inverse_kinematics(x_curr, x_new)

            # TODO: TEMP - MOVE ONLY POINTER, NO PA10
            self.env.set_group_pos('pointer', x_new)

            if constants.G_TABLE_IS_OSCILLATING:
                # Move the table with y-axis oscillation
                x_table_next = shaker_table(t, x_table)
            else:
                x_table_next = x_table

            self.env.set_body_pos('table', x_table_next)

            # Step through the world by 1 time frame and actuate pa10 joints
            self.env.performAction(pa10_joint_angles, fast=fast_step)

            # Update current time after this step
            t += dt_warped
            path_idx += 1

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
