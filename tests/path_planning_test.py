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

    training_filenames = [
        'staticgates/sample1.dat',
        'staticgates/sample2.dat',
        'staticgates/sample3.dat',

        #'randomgates/sample1.dat',
        #'randomgates/sample2.dat',
        #'randgates/sample3.dat',
    ]

    static_testing_filename = 'staticgates/sample4.dat'
    #random_testing_filename = 'randomgates/sample4.dat'

    # Get the training data and place it into a dataset
    training_dataset = None

    for training_filename in training_filenames:
        training_file = filepath + training_filename
        training_data = datastore.retrieve(training_file)

        training_dataset = datastore.list_to_dataset(
            training_data[:,:constants.G_LT_INPUTS],
            training_data[:,constants.G_TOTAL_INPUTS:],
            dataset=training_dataset
        )

    # Get testing data
    static_testing_file = filepath + static_testing_filename
    static_testing_data = datastore.retrieve(static_testing_file)

    static_testing_dataset = datastore.list_to_dataset(
        static_testing_data[:,:constants.G_LT_INPUTS],
        static_testing_data[:,constants.G_TOTAL_INPUTS:],
        dataset=None
    )

    #random_testing_file = filepath + random_testing_filename
    #random_testing_data = datastore.retrieve(random_testing_file)

    #random_testing_dataset = datastore.list_to_dataset(
    #    random_testing_data[:,:constants.G_LT_INPUTS],
    #    random_testing_data[:,constants.G_TOTAL_INPUTS:],
    #    dataset=None
    #)

    NUM_TRAINING_ITERATIONS = 100
    NUM_HIDDEN_NODES = 100
    WASHOUT_RATIO = 1.0 / 100.0

    print('>>> Building Network...')
    net = network.PathPlanningNetwork(
        indim=constants.G_LT_INPUTS,
        outdim=constants.G_LT_OUTPUTS,
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
    fig = plt.figure(1, facecolor='white')
    static_testing_axis = fig.add_subplot(111, projection='3d')
    #random_testing_axis = fig.add_subplot(122, projection='3d')

    fig.show()

    for idx in range(NUM_TRAINING_ITERATIONS):
        print('>>> Training (Iteration: %3d)...' % (idx+1))
        trainer.train()

        # Determine fitness of this network
        current_fitness = trainer.evaluation.max_fitness
        fitness_list.append(current_fitness)

        # Determine if this is the minimal error network
        if max_fitness is None or max_fitness < current_fitness:
            # This is the minimum, record it
            max_fitness = current_fitness
            max_fitness_epoch = idx

        # Draw the generated path after training
        print('>>> Testing Static Path...')
        _, generated_output, _ = net.calculateOutput(static_testing_dataset,
                washout_ratio=WASHOUT_RATIO)

        generated_input = static_testing_data[:len(generated_output),:constants.G_TOTAL_INPUTS]

        # Smash together the input and output
        generated_data = np.hstack((generated_input, generated_output))

        print('>>> Drawing Generated Static Path...')
        pathutils.display_path(static_testing_axis, generated_data, static_testing_data, title='Generated Static Path')

        #print('>>> Testing Random Path...')
        #_, generated_output, _ = net.calculateOutput(random_testing_dataset,
        #        washout_ratio=WASHOUT_RATIO)

        #generated_input = random_testing_data[:len(generated_output),:constants.G_TOTAL_INPUTS]

        ## Smash together the input and output
        #generated_data = np.hstack((generated_input, generated_output))

        #print('>>> Drawing Generated Random Path...')
        #pathutils.display_path(random_testing_axis, generated_data, random_testing_data, title='Generated Random Path')
        
        plt.draw()

    # Draw the iteration fitness plot
    plt.figure(facecolor='white')
    plt.cla()
    plt.title('Fitness of RNN over %d Iterations' % NUM_TRAINING_ITERATIONS)
    plt.xlabel('Training Iterations')
    plt.ylabel('Fitness')
    plt.grid(True)

    plt.plot(range(len(fitness_list)), fitness_list, 'r-')

    plt.annotate('local max', xy=(max_fitness_epoch, fitness_list[max_fitness_epoch]),
            xytext=(max_fitness_epoch, fitness_list[max_fitness_epoch]+0.01),
            arrowprops=dict(facecolor='black', shrink=0.05))

    plt.show()
