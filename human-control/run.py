#!/usr/bin/env python

import os
import ode
import numpy as np
import time

from model import HumanControlModel
from environment import HumanControlEnvironment
from controller import PhantomOmniInterface
from viewer import ViewerInterface


def run():
    step_count = 0

    paused = False
    stopped = False

    env = None
    omni = None
    kinematics = None

    (env, omni, kinematics) = init()

    t = 0.0 # [s]

    # Run the simulation at 60 frames per second
    fps = 60.0 # [Hz]
    dt = 1.0 / fps # [s]

    t_overshoot = 0.0

    print '>>> Running...'
    while not stopped:
        t_start = time.time()

        # If the last calculation took too long, catch up
        dt_warped = dt + t_overshoot

        env.set_dt(dt_warped)
        omni.set_dt(dt_warped)

        if paused:
            env.step(paused=True)
            continue

        # Populate the controller with the most up-to-date data
        omni.update()

        # Get the updated linear/angular velocities of the tooltip
        linear_vel = omni.get_linear_vel()
        angular_vel = omni.get_angular_vel()

        # Set the linear and angular velocities of the simulation
        env.set_group_linear_vel('pointer', linear_vel)
        env.set_group_angular_vel('pointer', angular_vel)

        # Step through the world by 1 time frame
        env.step()
        t += dt_warped

        # Determine the difference in virtual vs actual time
        t_warped = dt - (time.time() - t_start)

        # Attempt to enforce real-time constraints
        if t_warped >= 0.0:
            # The calculation took less time than the virtual time. Sleep the
            # rest off
            time.sleep(t_warped)
            t_overshoot = 0.0
        else:
            # The calculation took more time than the virtual time. We need to
            # catch up with the virtual time on the next time step
            t_overshoot = -t_warped

    return


def init():
    """Initialize Human Control Simulation

    Creates the environment, viewer, and (Phantom Omni) controller objects
    required to run the human data capture simulation.

    Returns:
        (env, omni, kinematics) - The three class objects used to run the
        simulation for human data capture.
    """
    xode_filename = 'model'

    # Generate the XODE file
    print '>>> Generating XODE'
    if os.path.exists('./'+xode_filename+'.xode'):
        os.remove('./'+xode_filename+'.xode')

    #xode_model = TestArmModel(xode_filename)
    xode_model = HumanControlModel(xode_filename)
    xode_model.writeXODE('./'+xode_filename)

    # Start environment
    print '>>> Starting Environment'
    env = HumanControlEnvironment('./'+xode_filename+'.xode', realtime=False)

    # Start viewer
    print '>>> Starting viewer'
    viewer = ViewerInterface()
    viewer.start()

    # Start controller
    print '>>> Starting Phantom Omni Interface'
    omni = PhantomOmniInterface()

    #ip = raw_input('<<< Enter host ip: ')
    #port = int(raw_input('<<< Enter tcp port: '))
    ip = '127.0.0.1'
    port = 5555

    # Try to connect to the Phantom Omni controller
    omni.connect(ip, port)

    # Start kinematics engine
    kinematics = None

    return (env, omni, kinematics)


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt as e:
        print '\n>>> Exiting main loop'
        ode.CloseODE()

    exit()
