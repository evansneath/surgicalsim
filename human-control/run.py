#!/usr/bin/env python

import os
import thread
import numpy as np

from model import TestArmModel
from environment import HumanControlEnvironment
from viewer import HumanControlViewer
from controller import HumanControlDevice


def run():
    step_count = 0

    paused = False
    stopped = False

    env = None
    viewer = None
    omni = None
    kinematics = None

    raw_data = []

    (env, omni, kinematics) = init()

    # TODO: Set the tooltip_pos_old and tooltop_rot_old here to the starting
    # position and rotation of the phantom omni device

    while not stopped:
        if paused:
            env.step(paused=True)
            continue

        # Get change of position/velocity of phantom omni
        tooltip_pos_new = omni.get_position()
        tooltip_rot_new = omni.get_rotation()

        # Use inverse kinematics to get joint torques
        torques = kinematics.get_torques(
            dt,
            tooltip_pos_old,
            tooltip_pos_new,
            tooltip_rot_old,
            tooltip_rot_new
        )

        # Apply torques to joints
        env.set_torques(torques)

        # Step through the world by 1 time frame
        env.step(paused=paused)

        # Store joint angles/velocities as raw data (env -> file)
        # raw_data.append((angles, velocities))

        tooltip_pos_old = np.copy(tooltip_pos_new)
        tooltip_rot_old = np.copy(tooltip_rot_new)

    # TODO: Perform cleanup stuff here

    return


def init():
    """Initialize Human Control Simulation

    Creates the environment, viewer, and (Phantom Omni) controller objects
    required to run the human data capture simulation.

    Returns:
        (env, viewer, omni) - The three class objects used to run the
        simulation for human data capture.
    """
    xode_filename = 'model'

    # Generate the XODE file
    if os.path.exists('./'+xode_filename+'.xode'):
        os.remove('./'+xode_filename+'.xode')

    #xode_filename = Pa10Model(xode_filename)
    xode_model = TestArmModel(xode_filename)
    xode_model.writeXODE('./'+xode_filename)

    # Start environment.
    env = HumanControlEnvironment('./'+xode_filename+'.xode')

    # Start viewer
    while True:
        env.step()

    # Start controller
    omni = HumanControlDevice()

    # Start kinematics engine
    return (env, omni, kinematics)


if __name__ == '__main__':
    run()
    exit()
