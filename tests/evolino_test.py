#!/usr/bin/env python

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from surgicalsim.lib.datastore import files_to_dataset
from surgicalsim.lib.network import NeuralNetwork


if __name__ == '__main__':
    # Build up the list of files to use as training set
    filepath = '/Users/evan/Workspace/surgicalsim/results/'
    filenames = ['out1.dat', 'out2.dat', 'out3.dat']
    filefullpaths = []

    for filename in filenames:
        filefullpaths.append(filepath+filename)

    wtRatio = 1.0 / 4.0

    training_dataset = files_to_dataset([filefullpaths[2]])
    training_sequence = training_dataset.getField('target')
    training_wt_idx = int(len(training_sequence) * wtRatio)
    training_washout = training_sequence[:training_wt_idx]
    training_target = training_sequence[training_wt_idx:]

    testing_dataset = files_to_dataset([filefullpaths[2]])
    testing_sequence = testing_dataset.getField('target')
    testing_wt_idx = int(len(testing_sequence) * wtRatio) 
    testing_washout = testing_sequence[:testing_wt_idx]
    testing_target =  testing_sequence[testing_wt_idx:]

    print('>>> Building Network...')
    net = NeuralNetwork(training_dataset)

    # Create a matplotlib figure for plotting
    plt.ion()

    training_counter = 0
    stop_every_x_epochs = 1000

    while True:
        print('>>> Training...')
        net.train()

        print('>>> Testing...')
        #from pybrain.datasets.sequential import SequentialDataSet
        #for i in np.arange(0.0, 10.0, 1.0/60.0):
        #    testing_dataset.addSample([], [])

        #out = net.test(testing_dataset)
        training_output = net.extrapolate(training_washout, len(training_target))
        testing_output = net.extrapolate(testing_washout, len(testing_target))
        
        # Draw the training data plot
        #sp = plt.subplot(211)
        #plt.cla()
        #plt.title('Training Data')

        training_xyz = zip(*testing_sequence)
        #plt.plot(training_xyz[0], training_xyz[2], 'b--')

        #training_output_xyz = zip(*training_output)
        #plt.plot(training_output_xyz[0], training_output_xyz[2], 'r-')

        # Draw the testing data plot
        sp = plt.subplot(111)
        plt.cla()
        plt.title('Testing Data')

        plt.plot(training_xyz[0], training_xyz[2], 'b--')

        testing_xyz = zip(*testing_output)
        plt.plot(testing_xyz[0], testing_xyz[2], 'r-')

        plt.draw()

        training_counter += 1

        if training_counter % stop_every_x_epochs == 0:
            raw_input('>>> Press <Enter> to Continue')
