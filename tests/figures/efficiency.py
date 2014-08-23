#!/usr/bin/env python2.7

import numpy as np

import surgicalsim.lib.constants as constants
import surgicalsim.lib.pathutils as pathutils
import surgicalsim.lib.datastore as datastore

"""
NOTE:
    This procedure was not used to calculate minimum possible traversal time.
    Instead, the time incrementally increased in the NeuralSim until the
    procedure passed. This was deemed the minimum feasible traversal time.
"""

def main():
    """
    OUTPUT THE MINIMUM REQUIRED TIME FOR THE RNN PATH TO COMPLETE
    """
    # Define generated data file name
    generated_file = '../../results/generated/efficiency-test.dat'

    # Collect path data from the file
    generated_path = datastore.retrieve(generated_file)

    # Calculate the indices of the end effector position columns
    pos_start_col = constants.G_POS_IDX
    pos_end_col = pos_start_col + constants.G_NUM_POS_DIMS

    # Assume time to complete path is 1 second
    dt = 1.0 / 60.0 # [s]
    t_total = (1.0 / dt) * float(len(generated_path))

    # Get the defined acceleration limit of the PA-10
    a_limit_norm = constants.G_MAX_ACCEL
    a_max_norm = 0.0

    x_curr = np.array([0.0, 0.0, 0.0])
    v_curr = np.array([0.0, 0.0, 0.0])

    for idx in xrange(len(generated_path)-1):
        # Get the tooltip position for this and the next sample
        x_curr = pathutils.get_path_tooltip_pos(generated_path, idx)
        x_next = pathutils.get_path_tooltip_pos(generated_path, idx+1)

        # Calculate the velocity from current to next sample
        v_next = (x_next - x_curr) / dt

        # Calculate the acceleration from current to next sample
        a = (v_next - v_curr) / dt
        a_norm = np.linalg.norm(a)

        # Store this acceleration if it's greater than the current max
        if a_norm > a_max_norm:
            a_max_norm = a_norm

        # Set the current to the next velocity
        v_curr = v_next.copy()

    print('dt: %f [s]' % dt)
    print('a_max: %f [m/s^2]' % a_max_norm)

    # Calculate the gain factor needed to bring the max norm acceleration to
    # the acceleration norm limit
    a_gain = a_limit_norm / a_max_norm

    print('gain_factor: %f' % a_gain)

    return


if __name__ == '__main__':
    main()
    exit()
