#!/usr/bin/env python

import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
import numpy as np

from surgicalsim.lib.datastore import files_to_dataset, xyz_to_dataset
from surgicalsim.lib.network import NeuralNetwork


if __name__ == '__main__':
    # Build up the list of files to use as training set
    filepath = '/Users/evan/Workspace/surgicalsim/results/'
    filenames = ['out1_trimmed.dat', 'out2.dat', 'out3.dat']
    filefullpaths = []

    for filename in filenames:
        filefullpaths.append(filepath+filename)

    wtRatio = 1.0 / 10.0

    training_dataset = files_to_dataset([filefullpaths[2]])

    training_sequence = training_dataset.getField('target')

    # Trim up the training dataset
    training_sequence = training_sequence[120:-55]

    training_wt_idx = int(len(training_sequence) * wtRatio)
    training_washout = training_sequence[:training_wt_idx]
    training_target = training_sequence[training_wt_idx:]

    testing_dataset = files_to_dataset([filefullpaths[2]])
    testing_sequence = testing_dataset.getField('target')

    # Trim up the testing dataset
    testing_sequence = testing_sequence[120:-55]

    testing_wt_idx = int(len(testing_sequence) * wtRatio) 
    testing_washout = testing_sequence[:testing_wt_idx]
    testing_target =  testing_sequence[testing_wt_idx:]

    print('>>> Building Network...')
    trimmed_training_dataset = xyz_to_dataset(testing_sequence)
    net = NeuralNetwork(trimmed_training_dataset)

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
        #from pybrain.datasets.sequential import SequentialDataSet
        #for i in np.arange(0.0, 10.0, 1.0/60.0):
        #    testing_dataset.addSample([], [])

        #training_output = net.extrapolate(training_washout, len(training_target))
        testing_output = net.extrapolate(testing_washout, len(testing_target))
       
        # Calculate the RMS error of the testing set
        print('>>> Calculating RMS Error...')
        this_rms = np.sqrt(np.mean((testing_output - testing_target) ** 2))
        rms_errors.append(this_rms)

        # Determine if this is the minimal error network
        if min_error is None or min_error > this_rms:
            # This is the minimum, record it
            min_error = this_rms
            min_error_index = idx
            min_error_output = testing_output

    plt.figure(1, facecolor='white')
    plt.title('Figure 1: Path planning over %d iterations' % iterations)

    # Draw the training data plot
    training_xyz = zip(*training_sequence)

    plt.subplot(121, autoscale_on=False, aspect='equal')
    plt.cla()
    plt.title('Training Data')
    plt.xlabel('Position X Axis [m]')
    plt.ylabel('Position Z Axis [m]')
    plt.plot(training_xyz[0], -np.array(training_xyz[2]), 'b--')

    testing_xyz = zip(*testing_sequence)
    output_xyz = zip(*min_error_output)

    # Draw the testing data plot
    plt.subplot(122, autoscale_on=False, aspect='equal')
    plt.cla()
    plt.title('Testing Data (Minimal RMS Error)')
    plt.xlabel('Position X Axis [m]')
    plt.ylabel('Position Z Axis [m]')
    plt.plot(output_xyz[0], -np.array(output_xyz[2]), 'r-')

    # Draw the RMS error plot
    plt.figure(2, facecolor='white')
    plt.subplot(111)
    plt.cla()
    plt.title('RMS Error of RNN Training over %d Iterations' % iterations)
    plt.xlabel('Training Iterations')
    plt.ylabel('RMS Error [m]')
    plt.grid(True)
    plt.plot(range(len(rms_errors)), rms_errors, 'r--')

    plt.annotate('local min', xy=(min_error_index, rms_errors[min_error_index]),
            xytext=(min_error_index, rms_errors[min_error_index]+0.01),
            arrowprops=dict(facecolor='black', shrink=0.05))

    plt.show()
