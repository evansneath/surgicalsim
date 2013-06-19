#!/usr/bin/env python

from pa10 import Pa10Xode, Pa10Environment, Pa10MovementTask

from pybrain.structure.modules.tanhlayer import TanhLayer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.rl.agents import OptimizationAgent
from pybrain.optimization import PGPE
from pybrain.rl.experiments import EpisodicExperiment

import os.path


def create_environment():
    # Generate the xode file for world creation
    xode_name = 'pa10'

    if os.path.exists('./'+xode_name+'.xode'):
        os.remove('./'+xode_name+'.xode')

    xode = Pa10Xode(xode_name)
    xode.writeXODE('./'+xode_name)

    # Create the environment
    env = Pa10Environment(xodeFile='./'+xode_name+'.xode')

    return env


def run_forever(env):
    # Continue this simulation forever without resets
    while True:
        env.step()

    return


def run_experiment(env, task):
    # Create the controller network
    hiddenUnits = 4
    net = buildNetwork(len(task.getObservation()), hiddenUnits, env.actLen, outclass=TanhLayer)

    # Create the learning agent
    agent = OptimizationAgent(net, PGPE(storeAllEvaluations=True))

    # Create the experiment
    experiment = EpisodicExperiment(task, agent)

    # Run the experiment
    episodes = 40
    for episode in range(episodes):
        experiment.doEpisodes(1)

    return


if __name__ == '__main__':
    env = create_environment()
    task = Pa10MovementTask(env)
    run_experiment(env, task)
    #run_forever(env)
