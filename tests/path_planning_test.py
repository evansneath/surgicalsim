#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import surgicalsim.lib.constants as constants
import surgicalsim.lib.pathutils as pathutils
import surgicalsim.lib.datastore as datastore
import surgicalsim.lib.network as network


if __name__ == '__main__':
    # Build up the list of files to use as training set
    filepath = '/Users/evan/Workspace/surgicalsim/results/'
    filenames = ['sample1.dat', 'sample2.dat']

    filefullpaths = []
    all_training_data = None

    # Collect all training data and place it in a 3D array: [t, data, dataset]
    for filename in filenames:
        if all_training_data is None:
            all_training_data = datastore.retrieve(filename)
        else:
            all_training_data = np.dstack(all_training_data,
                    datastore.retrieve(filename))

    training_dataset = datastore.files_to_dataset(filefullpaths,
            constants.G_TOTAL_INPUTS)

    print('>>> Building Network...')
    net = network.PathPlanningNetwork()

    # TODO: Set the training dataset as the RNN dataset

    iterations = 100

    rms_errors = []
    min_error = None
    min_error_index = None
    min_error_output = None

    for idx in range(iterations):
        print('---------- ITERATION %3d ----------' % (idx + 1))
        print('>>> Training...')
        net.train()

        print('>>> Testing...')
        net.test()
      
        # Calculate the RMS error of the testing set
        print('>>> Calculating RMS Error...')
        this_rms = np.sqrt(np.mean((generated_path - ) ** 2))
        rms_errors.append(this_rms)

        # Determine if this is the minimal error network
        if min_error is None or min_error > this_rms:
            # This is the minimum, record it
            min_error = this_rms
            min_error_index = idx
            min_error_output = testing_output

    # Define figure 1
    plt.figure(121, facecolor='white')
    
    # Draw the training data plot

    # TODO: GET training_path
    axis1 = plt.subplot(1, projection='3d')
    pathutils.display_path(axis1, training_path, title='Training Path')

    # Draw the testing data plot

    # TODO: GET generated_path
    axis2 = plt.subplot(2, projection='3d')
    pathutils.display_path(axis2, generated_path, title='Generated Path')

    # Draw the RMS error plot
    plt.figure(facecolor='white')
    plt.cla()
    plt.title('RMS Error of RNN Training over %d Iterations' % iterations)
    plt.xlabel('Training Iterations')
    plt.ylabel('RMS Error [m]')
    plt.grid(True)
    plt.plot(range(len(rms_errors)), rms_errors, 'r-')

    plt.annotate('local min', xy=(min_error_index, rms_errors[min_error_index]),
            xytext=(min_error_index, rms_errors[min_error_index]+0.01),
            arrowprops=dict(facecolor='black', shrink=0.05))

    plt.show()
