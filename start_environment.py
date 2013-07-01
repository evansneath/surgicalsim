#!/usr/bin/env python

from pa10 import Pa10Xode, Pa10BallXode, Pa10Environment, Pa10MovementTask

from pybrain.optimization import PGPE
from pybrain.structure.modules.tanhlayer import TanhLayer
from pybrain.rl.agents import OptimizationAgent
from pybrain.rl.experiments import EpisodicExperiment
from pybrain.tools.example_tools import ExTools
from pybrain.tools.shortcuts import buildNetwork

import os.path

import numpy as np


def create_environment():
    # Generate the xode file for world creation
    xode_name = 'pa10'

    if os.path.exists('./'+xode_name+'.xode'):
        os.remove('./'+xode_name+'.xode')

    #xode = Pa10Xode(xode_name)
    xode = Pa10BallXode(xode_name)
    xode.writeXODE('./'+xode_name)

    # Create the environment
    env = Pa10Environment(xodeFile='./'+xode_name+'.xode')

    return env


def run_forever():
    # Create the environment
    env = create_environment()

    # Continue this simulation forever without resets
    while True:
        env.step()

    return


def run_experiment():
    # Create the controller network
    HIDDEN_NODES = 4

    RUNS = 10
    BATCHES = 1
    PRINTS = 1
    EPISODES = 200

    env = None

    run_results = []

    # Set up plotting tools for the experiments
    tools = ExTools(BATCHES, PRINTS)

    # Run the experiment
    for run in range(RUNS):
        # If an environment already exists, shut it down
        if env:
            env.closeSocket()

        # Create the environment
        env = create_environment()

        # Create the task
        task = Pa10MovementTask(env)

        new_hidden_nodes = HIDDEN_NODES + run

        # Create the neural network
        net = buildNetwork(len(task.getObservation()), new_hidden_nodes, env.actLen, outclass=TanhLayer)

        # Create the learning agent
        agent = OptimizationAgent(net, PGPE(storeAllEvaluations=True))
        tools.agent = agent

        # Create the experiment
        experiment = EpisodicExperiment(task, agent)

        for episode in range(EPISODES):
            experiment.doEpisodes(BATCHES)
            tools.printResults((agent.learner._allEvaluations)[-50:-1], run, episode)
            print agent.learner._allEvaluations

        #tools.addExps()

        all_results = agent.learner._allEvaluations
        max_result = np.max(all_results)
        avg_result = np.sum(all_results) / len(all_results)
        run_results.append((run, max_result, avg_result))

    #tools.showExps()

    # Print the results table
    for result in run_results:
        print 'RUN: %d' % result[0]
        print 'MAX: %4f' % result[1]
        print 'AVG: %4f\n' % result[2]

    return


if __name__ == '__main__':
    run_experiment()
    #run_forever()
