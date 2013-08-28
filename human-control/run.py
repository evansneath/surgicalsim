#!/usr/bin/env python

"""Run module

Acts as the main event loop and command line interface for the Surgical Sim
test article training simulator.

Author:
    Evan Sneath - evansneath@gmail.com

License:
    Open Software License v3.0

Functions:
    parse_arguments: Parses incoming command line arguments.
    main: Initializes all objects and begins the main event loop.
"""

# Import all external modules
import argparse
import os
import numpy as np
import time
import cPickle

# Import all application modules
from model import HumanControlModel
from environment import HumanControlEnvironment
from controller import PhantomOmniInterface
from viewer import ViewerInterface


# Define all global objects
g_tooltip_data = []

g_env = None
g_omni = None
g_kinematics = None
g_viewer = None


def main():
    """Main

    The main driver function responsible for initializing, running the event
    loop, and closing the application on exit.
    """
    args = parse_arguments()
    
    try:
        # Initialize all module of the simulation
        print '>>> Initializing...'
        _init(args)

        # Continue to execute the main simulation loop
        print '>>> Running... (ctrl+c to exit)'
        _event_loop()
    except KeyboardInterrupt as e:
        # Except the keyboard interrupt as the valid way of leaving the event
        # loop for now
        print '\n>>> Writing captured data'
        _write_data(args.outfile)

        print '>>> Cleaning up...'
        _clean_up()

        print '>>> Exiting'

    return


def parse_arguments():
    """Parse Arguments

    Parsers all command line arguments for the application.

    Returns:
        An object containing all expected command line arguments.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-v', '--verbose', action='store_true',
            help='show additional output information at runtime'
    )
    parser.add_argument(
            '-r', '--randomize', action='store_true',
            help='randomize test article gate placement'
    )
    parser.add_argument(
            '-n', '--network', action='store_true',
            help='controller is non-local. ip/port info will be prompted'
    )
    parser.add_argument(
            '-o', '--outfile', action='store', default='out.dat',
            help='target path for the tooltip pickled data'
    )

    args = parser.parse_args()

    return args


def _init(args):
    """Initialize Human Control Simulation

    Creates the environment, viewer, and (Phantom Omni) controller objects
    required to run the human data capture simulation.

    Globals:
        g_env: The ODE simulation environment class object.
        g_omni: The Phantom Omni controller interface class object.
        g_kinematics: The PA10 kinematic simulator class object.
        g_viewer: The OpenGL viewer interface class object.

    Arguments:
        args: An argparse object containing all valid command line arguments.
    """
    global g_env
    global g_omni
    global g_kinematics
    global g_viewer

    xode_filename = 'model'

    # Generate the XODE file
    print '>>> Generating world model'
    if os.path.exists('./'+xode_filename+'.xode'):
        os.remove('./'+xode_filename+'.xode')

    xode_model = HumanControlModel(
            name=xode_filename,
            randomize_test_article=args.randomize
    )
    xode_model.generate()

    # Start environment
    print '>>> Starting environment'
    g_env = HumanControlEnvironment(
            xode_filename='./'+xode_filename+'.xode',
            realtime=False,
            verbose=args.verbose
    )

    # Start viewer
    print '>>> Starting viewer'
    g_viewer = ViewerInterface(verbose=args.verbose)
    g_viewer.start()

    # Start controller
    print '>>> Starting Phantom Omni interface'
    g_omni = PhantomOmniInterface()

    if args.network:
        ip = raw_input('<<< Enter host ip: ')
        port = int(raw_input('<<< Enter tcp port: '))
    else:
        ip = '127.0.0.1'
        port = 5555

    # Try to connect to the Phantom Omni controller
    g_omni.connect(ip, port)

    # Start kinematics engine
    g_kinematics = None

    return


def _event_loop():
    """Event Loop

    The main application loop where the simulation is stepped through every
    'dt' seconds. Real-time constraints are enforced by simulation time warp.

    Globals:
        g_env: The ODE simulation environment class object.
        g_omni: The Phantom Omni controller interface class object.
        g_kinematics: The PA10 kinematic simulator class object.
        g_viewer: The OpenGL viewer interface class object.
        g_tooltip_data: The tooltip data for each simulation time step.
    """
    global g_env
    global g_omni
    global g_kinematics
    global g_viewer
    global g_tooltip_data

    paused = False
    stopped = False

    # Define the simulation frame rate
    fps = 60.0 # [Hz]
    dt = 1.0 / fps # [s]

    # Keep track of time overshoot in the case that simulation time must be
    # increased in order to maintain real-time constraints
    t_overshoot = 0.0

    while not stopped:
        t_start = time.time()

        # If the last calculation took too long, catch up
        dt_warped = dt + t_overshoot

        g_env.set_dt(dt_warped)
        g_omni.set_dt(dt_warped)

        # TODO: Update the viewer with the latest control signals
        #viewer.update()

        if paused:
            g_env.step(paused=True)
            continue

        # Populate the controller with the most up-to-date data
        g_omni.update()

        # Record the positional and angular tooltip data
        data_pack = (g_omni.get_pos().tolist(), g_omni.get_angle().tolist())
        g_tooltip_data.append(data_pack)

        # Get the updated linear/angular velocities of the tooltip
        linear_vel = g_omni.get_linear_vel()
        angular_vel = g_omni.get_angular_vel()

        # Set the linear and angular velocities of the simulation
        g_env.set_group_linear_vel('pointer', linear_vel)
        g_env.set_group_angular_vel('pointer', angular_vel)

        # Step through the world by 1 time frame
        g_env.step()

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


def _write_data(outfile):
    """Write Data

    Writes all data written to the global g_tooltip_data into the specified
    output file in a pickled format.

    Globals:
        g_tooltip_data: An array of data from each simulation time step.
    """
    with open(outfile, 'w+') as f:
        cPickle.dump(g_tooltip_data, f)

    return


def _clean_up():
    """Clean Up

    Attempts to shut down any active engines and kills off spawned processes
    and class objects.

    Globals
        g_viewer: The OpenGL viewer interface class object.
        g_env: The ODE simulation environment class object.
        g_omni: The Phantom Omni controller interface class object.
    """
    # Kill the viewer process
    if g_viewer is not None:
        g_viewer.stop()

    # Kill the ODE environment objects
    if g_env is not None:
        g_env.stop()

    # Kill the controller process
    if g_omni is not None:
        g_omni.disconnect()

    return


if __name__ == '__main__':
    main()
