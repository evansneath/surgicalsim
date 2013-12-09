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
    process_path: Trims and normalizes input path data.
    main: Initializes all objects and begins the main event loop.
"""


# Import external modules
import argparse

# Import application modules
from simulation import TrainingSimulation

import surgicalsim.lib.constants as constants
import surgicalsim.lib.pathutils as pathutils
import surgicalsim.lib.datastore as datastore


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


def process_path(data):
    """Process Path

    Given raw data from TrainingSim, the trimmming wizard prompts the user to
    modify the start/end of the path. The time dimension of the path is then
    normalized.

    Arguments:
        data: Raw numpy data array from the TrainingSim application.

    Returns:
        Processed numpy data array that is trimmed and time-normalized.
    """
    # Prompt the user to trim the start and end of the path
    data = pathutils.trim_path(data)

    # Normalize the time dimension of the data between 0.0 and 1.0
    data = pathutils.normalize_time(data, t_col=constants.G_TIME_IDX)

    # Prompt the user to rate all detected segments of the path
    data = pathutils.rate_segments(data)

    return data


def main():
    """Main

    The main driver function responsible for initializing, running the event
    loop, and closing the application on exit.
    """
    args = parse_arguments()

    sim = None
    
    try:
        # Initialize all module of the simulation
        print '>>> Initializing...'
        sim = TrainingSimulation(args.randomize, args.network, args.verbose)

        # Continue to execute the main simulation loop
        print '>>> Running... (ctrl+c to exit)'
        sim.start()
    except KeyboardInterrupt as e:
        # Except the keyboard interrupt as the valid way of leaving the loop
        if sim is not None and len(sim.saved_data):
            print '\n>>> Processing path data...'
            path = process_path(sim.saved_data)

            print '\n>>> Writing path data to %s' % args.outfile
            datastore.store(path, args.outfile)

        print '>>> Cleaning up...'
        del sim

        print '>>> Exiting'

    return


if __name__ == '__main__':
    main()
