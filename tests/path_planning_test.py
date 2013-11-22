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
    training_filenames = ['sample1.dat', 'sample2.dat']
    testing_filename = 'sample3.dat'

    # Get the training data and place it into a dataset
    training_dataset = None

    for filename in training_filenames:
        file = filepath + filename

        training_dataset = datastore.files_to_dataset(
            [file],
            constants.G_TOTAL_INPUTS,
            dataset=training_dataset
        )

    # Get testing data and strip it out any output
    testing_file = filepath + testing_filename

    testing_dataset = datastore.files_to_dataset(
        [testing_file],
        constants.G_TOTAL_INPUTS,
        dataset=None
    )

    NUM_TRAINING_ITERATIONS = 100
    NUM_HIDDEN_NODES = 40
    WASHOUT_RATIO = 1.0 / 10.0

    print('>>> Building Network...')
    net = network.PathPlanningNetwork(
        indim=constants.G_TOTAL_INPUTS,
        outdim=constants.G_TOTAL_OUTPUTS,
        hiddim=NUM_HIDDEN_NODES
    )

    print('>>> Initializing Trainer...')
    trainer = network.PathPlanningTrainer(
        evolino_network=net,
        dataset=training_dataset,
        wtRatio=WASHOUT_RATIO
    )

    # Begin the training iterations
    fitness_list = []
    max_fitness = None
    max_fitness_epoch = None

    # Draw the generated path plot
    fig = plt.figure(facecolor='white')
    testing_axis = fig.gca(projection='3d')

    for idx in range(NUM_TRAINING_ITERATIONS):
        print('>>> Training (Iteration: %3d)...' % (idx+1))
        trainer.train()

        # Determine fitness of this network
        current_fitness = trainer.evaluation.max_fitness
        fitness_list.append(current_fitness)

        # Determine if this is the minimal error network
        if max_fitness is None or max_fitness > current_fitness:
            # This is the minimum, record it
            max_fitness = current_fitness
            max_fitness_epoch = idx

        # Draw the generated path after training
        print('>>> Testing...')
        generated_input, generated_output, _ = net.calculateOutput(testing_dataset,
                washout_ratio=WASHOUT_RATIO)

        # Smash together the input and output
        generated_path = np.hstack((generated_input, generated_output))

        pathutils.display_path(testing_axis, generated_path, title='Generated Path')
        plt.draw()

    # Draw the iteration fitness plot
    plt.figure(facecolor='white')
    plt.cla()
    plt.title('Fitness of RNN over %d Iterations' % NUM_TRAINING_ITERATIONS)
    plt.xlabel('Training Iterations')
    plt.ylabel('Fitness')
    plt.grid(True)

    plt.plot(range(len(fitness_list)), fitness_list, 'r-')

    plt.annotate('local min', xy=(max_fitness_epoch, fitness_list[max_fitness_epoch]),
            xytext=(max_fitness_epoch, fitness_list[max_fitness_epoch]+0.01),
            arrowprops=dict(facecolor='black', shrink=0.05))

    plt.show()
