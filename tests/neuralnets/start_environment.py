#!/usr/bin/env python

from pa10 import Pa10BallXode, Pa10Environment, Pa10MovementTask

from pybrain.optimization import PGPE, HillClimber
from pybrain.structure.modules.tanhlayer import TanhLayer

from pybrain.rl.learners import Q
from pybrain.rl.agents import OptimizationAgent, LearningAgent
from pybrain.rl.experiments import EpisodicExperiment

from pybrain.tools.example_tools import ExTools
from pybrain.tools.shortcuts import buildNetwork

import os.path

import numpy as np

G_RESULTS_DIR = 'results'

def create_environment():
    """Create Simulation Environment

    Generates and initializes the PA10 robotic arm environment from
    the specifications defined in ./pa10/xode.py.

    Returns:
        The ODE environment for the PA10 robotic arm.
    """
    # Generate the xode file for world creation
    xode_name = 'pa10'

    if os.path.exists('./'+xode_name+'.xode'):
        os.remove('./'+xode_name+'.xode')

    xode = Pa10BallXode(xode_name)
    xode.writeXODE('./'+xode_name)

    # Create the environment
    env = Pa10Environment(xodeFile='./'+xode_name+'.xode')

    return env


def create_network(in_nodes, hidden_nodes, out_nodes):
    """Create Artificial Neural Network

    Arguments:
        in_nodes: The number of input nodes in the network.
        hidden_nodes: The number of hidden nodes in the network.
        out_nodes: The number of output nodes in the network.

    Returns:
        The artificial neural network module.
    """
    net = buildNetwork(in_nodes, hidden_nodes, out_nodes, outclass=TanhLayer, recurrent=True)
    return net


def run_forever():
    env = create_environment()

    # Continue this simulation forever without resets
    while True:
        env.step()

    return


def run_experiment():
    # Create the controller network
    HIDDEN_NODES = 4

    RUNS = 2
    BATCHES = 1
    PRINTS = 1
    EPISODES = 500

    env = None
    start_state_net = None

    run_results = []

    # Set up plotting tools for the experiments
    tools = ExTools(BATCHES, PRINTS)

    # Run the experiment
    for run in range(RUNS):
        if run == 0:
            continue

        # If an environment already exists, shut it down
        if env:
            env.closeSocket()

        # Create the environment
        env = create_environment()

        # Create the task
        task = Pa10MovementTask(env)

        # Create the neural network. Only create the network once so it retains
        # the same starting values for each run.
        if start_state_net:
            net = start_state_net.copy()
        else:
            # Create the initial neural network
            net = create_network(
                    in_nodes=env.obsLen,
                    hidden_nodes=HIDDEN_NODES,
                    out_nodes=env.actLen
            )
            start_state_net = net.copy()

        # Create the learning agent
        learner = HillClimber(storeAllEvaluations=True)
        agent = OptimizationAgent(net, learner)
        tools.agent = agent

        # Create the experiment
        experiment = EpisodicExperiment(task, agent)

        # Perform all episodes in the run
        for episode in range(EPISODES):
            experiment.doEpisodes(BATCHES)

        # Calculate results
        all_results = agent.learner._allEvaluations
        max_result = np.max(all_results)
        min_result = np.min(all_results)
        avg_result = np.sum(all_results) / len(all_results)
        run_results.append((run, max_result, min_result, avg_result))

        # Make the results directory if it does not exist
        if not os.path.exists(G_RESULTS_DIR):
            os.mkdir(G_RESULTS_DIR)

        # Write all results to the results file
        with open(os.path.join(G_RESULTS_DIR, 'run_%d.txt' % run), 'w+') as f:
            # Store the calculated max, min, avg
            f.write('RUN, MAX, MIN, AVG\n')
            f.write('%d, %f, %f, %f\n' % (run, max_result, min_result, avg_result))

            # Store all results from this run
            f.write('EPISODE, REWARD\n')
            for episode, result in enumerate(all_results):
                f.write('%d, %f\n' % (episode, result))

    return


if __name__ == '__main__':
    run_experiment()
