#!/usr/bin/env python

import os
import ode
import numpy as np
import time

from model import TestArmModel, EndEffectorModel
from environment import HumanControlEnvironment
from controller import HumanControlDevice


def run():
    step_count = 0

    paused = False
    stopped = False

    env = None
    omni = None
    kinematics = None

    (env, omni, kinematics) = init()

    t = 0.0 # [s]
    dt = 0.005 # [s]

    env.set_dt(dt)
    omni.set_dt(dt)

    #omni.set_initial_pos(env.init_body_positions['tooltip'])
    time.sleep(1)

    print '>>> Running...'
    while not stopped:
        if paused:
            env.step(paused=True)
            continue

        omni.update()

        linear_vel = omni.get_linear_vel()
        angular_vel = omni.get_angular_vel()

        env.set_group_linear_vel('pointer', linear_vel)
        env.set_group_angular_vel('pointer', angular_vel)

        # Step through the world by 1 time frame
        env.step()

        t += dt


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
    print '>>> Generating XODE'
    if os.path.exists('./'+xode_filename+'.xode'):
        os.remove('./'+xode_filename+'.xode')

    #xode_model = TestArmModel(xode_filename)
    xode_model = EndEffectorModel(xode_filename)
    xode_model.writeXODE('./'+xode_filename)

    # Start environment.
    print '>>> Starting Environment'
    env = HumanControlEnvironment('./'+xode_filename+'.xode')

    # Start controller
    print '>>> Starting Controller'
    omni = HumanControlDevice()

    # Start kinematics engine
    kinematics = None

    return (env, omni, kinematics)


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt as e:
        print '\n>>> Exiting'
        ode.CloseODE()

    exit()
