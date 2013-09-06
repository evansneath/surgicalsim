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


# Import external modules
import argparse

# Import application modules
from lib.simulation import Simulation


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
        sim = Simulation(args.randomize, args.network, args.verbose)

        # Continue to execute the main simulation loop
        print '>>> Running... (ctrl+c to exit)'
        sim.start()
    except KeyboardInterrupt as e:
        # Except the keyboard interrupt as the valid way of leaving the loop
        if sim is not None:
            print '\n>>> Writing captured data'
            sim.write_data(args.outfile)

        print '>>> Cleaning up...'
        del sim

        print '>>> Exiting'

    return


if __name__ == '__main__':
    main()
