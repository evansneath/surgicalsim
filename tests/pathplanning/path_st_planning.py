#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import surgicalsim.lib.constants as constants
import surgicalsim.lib.pathutils as pathutils
import surgicalsim.lib.datastore as datastore
import surgicalsim.lib.network as network


if __name__ == '__main__':
    # Define testing constants
    NUM_TRAINING_ITERATIONS = 100
    NUM_HIDDEN_NODES = 10

    # Get short term path segments from multiple paths
    filepath = '/Users/evan/Workspace/surgicalsim/results/'

    training_filenames = [
        'sample1.dat',
        'sample2.dat',
        'sample3.dat',
        'sample4.dat',
    ]

    testing_filename = 'sample5.dat'

    # Build a training dataset from all training file data
    training_dataset = None

    for training_filename in training_filenames:
        training_file = filepath + training_filename
        training_data = datastore.retrieve(training_file)

        # Split the file into gate segments
        training_segments = pathutils.split_segments(training_data)

        # Add each segment as a new entry in the dataset
        for gate, path in enumerate(training_segments):
            # Get short-term training inputs
            input_start_idx = constants.G_ST_INPUT_IDX + (gate * constants.G_NUM_GATE_DIMS)
            input_end_idx = start_input_idx + constants.G_ST_NUM_INPUTS
            input = path[:,start_input_idx:end_input_idx]

            # Get short-term training outputs
            output_start_idx = constants.G_G_ST_OUTPUT_IDX
            output_end_idx = output_start_idx + constants.G_ST_NUM_OUTPUTS
            output = path[:,output_start_idx:output_end_idx],

            # Convert input and output sequence to dataset object
            training_dataset = datastore.list_to_dataset(
                input,
                output,
                dataset=training_dataset
            )

    # Build a testing dataset
    testing_dataset = None

    for gate, path in enumerate(testing_segments):
        input_start_idx = constants.G_ST_INPUT_IDX + (gate * constants.G_NUM_GATE_DIMS)
        input_end_idx = start_input_idx + constants.G_ST_NUM_INPUTS
        input = path[:,start_input_idx:end_input_idx]

        # Get short-term training outputs
        output_start_idx = constants.G_G_ST_OUTPUT_IDX
        output_end_idx = output_start_idx + constants.G_ST_NUM_OUTPUTS
        output = path[:,output_start_idx:output_end_idx],

        testing_dataset = datastore.list_to_dataset(
            input,
            output,
            dataset=testing_dataset
        )

    # Create recurrent neural network
    print('>>> Building Network...')
    net = network.ShortTermPlanningNetwork(
        indim=constants.G_ST_NUM_INPUTS,
        outdim=constants.G_ST_NUM_OUTPUTS,
        hiddim=NUM_HIDDEN_NODES
    )

    print('>>> Initializing Trainer...')
    trainer = network.ShortTermPlanningTrainer(
        net,
        dataset=training_datset,
        #learningrate=0.1,
        #lrdecay=1.0,
        #momentum=0.0,
        #verbose=False,
        #batchlearning=False,
        #weightdecay=0.0,
    )

    for idx in range(NUM_TRAINING_ITERATIONS):
        trainer.train()
