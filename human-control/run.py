#!/usr/bin/env python

import os
import thread
import numpy as np

from model import TestArmModel, EndEffectorModel
from environment import HumanControlEnvironment
from controller import HumanControlDevice

import time

def run():
    step_count = 0

    paused = False
    stopped = False

    env = None
    omni = None
    kinematics = None

    (env, omni, kinematics) = init()

    cur_time = 0
    env.dt = 0.005

    while not stopped:
        if paused:
            env.step(paused=True)
            continue

        # TODO: Uncomment this once Omni controls are working
        #next_pos = omni.get_pos()
        next_pos = oscillation_test(cur_time, env)
        env.set_group_pos('pointer', next_pos)

        # Step through the world by 1 time frame
        env.step()
        cur_time += env.dt

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

    # Start kinematics engine
    kinematics = None

    return (env, omni, kinematics)


def oscillation_test(cur_time, env):
    """Oscillation Test

    Oscillates the tooltip in the x and y direction.
    x_amp, y_amp, x_freq, and y_freq and adjustable parameters to control
    the sinusoidal oscillations from the starting position.
    """
    amps = np.array([0.1, 0.1, 0.1])
    freqs = np.array([0.4, 0.2, 0.1])
    pos = amps * np.sin(2.0 * np.pi * cur_time * freqs)

    return pos


if __name__ == '__main__':
    run()
    exit()
