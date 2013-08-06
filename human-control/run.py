#!/usr/bin/env python

import os
import thread
import numpy as np

from model import TestArmModel, EndEffectorModel
from environment import HumanControlEnvironment
from viewer import HumanControlViewer
from controller import HumanControlDevice

import time

def run():
    step_count = 0

    paused = False
    stopped = False

    env = None
    omni = None
    kinematics = None

    raw_data = []

    (env, omni, kinematics) = init()

    # TODO: Set the tooltip_pos_old and tooltop_rot_old here to the starting
    # position and rotation of the phantom omni device
    cur_time = 0
    env.dt = 0.005

    while not stopped:
        if paused:
            env.step(paused=True)
            continue

        #omni.update()
        #env.set_body_pos('tooltip', tuple(omni.pos))

        #oscillation_test(cur_time, env)
        pos = omni.get_pos()
        increment_pos(env, pos)

        # Step through the world by 1 time frame
        env.step()
        cur_time += env.dt

        # Store joint angles/velocities as raw data (env -> file)
        # raw_data.append((angles, velocities))

        #tooltip_pos_old = np.copy(tooltip_pos_new)
        #tooltip_rot_old = np.copy(tooltip_rot_new)

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

    #xode_model = Pa10Model(xode_filename)
    #xode_model = TestArmModel(xode_filename)
    xode_model = EndEffectorModel(xode_filename)
    xode_model.writeXODE('./'+xode_filename)

    # Start environment.
    env = HumanControlEnvironment('./'+xode_filename+'.xode')

    # Start controller
    omni = HumanControlDevice()
    omni.start()

    # Start kinematics engine
    kinematics = None

    return (env, omni, kinematics)


def oscillation_test(cur_time, env):
    x_new = 1.0 * np.sin(2.0 * np.pi * cur_time / 25.0)
    (x_stick, y_stick, z_stick) = env.get_body_pos('stick')
    (x_tooltip, y_tooltip, z_tooltip) = env.get_body_pos('tooltip')

    env.set_body_pos('stick', (x_new, y_stick, z_stick))
    env.set_body_pos('tooltip', (x_new, y_tooltip, z_tooltip))
    return


def increment_pos(env, pos):
    pos = np.array(pos)

    stick_pos = np.array(env.get_body_pos('stick'))
    tooltip_pos = np.array(env.get_body_pos('tooltip'))

    stick_pos_new = stick_pos + pos
    tooltip_pos_new = tooltip_pos + pos

    env.set_body_pos('stick', tuple(stick_pos_new))
    env.set_body_pos('tooltip', tuple(tooltip_pos_new))
    
    return


if __name__ == '__main__':
    run()
    exit()
