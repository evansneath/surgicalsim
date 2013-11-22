#!/usr/bin/env python

"""Network module

Contains the neural network class for regression training and testing of the
surgicalsim environment.

Author:
    Evan Sneath - evansneath@gmail.com

License:
    Open Software License v3.0

Classes:
    PathPlanningNetwork: Artificial neural networks class for path prediction.
    PathPlanningTrainer: Neural network trainer for path prediction network.
"""


# Import pybrain neural network modules
from pybrain.supervised.evolino.networkwrapper import EvolinoNetwork
from pybrain.supervised.trainers.evolino import EvolinoTrainer


class PathPlanningNetwork(EvolinoNetwork):
    """PathPlanningNetwork class

    The primary path planning network for the surgicalsim testing environment.

    Inherits:
        EvolinoNetwork: The PyBrain built-in Evolino network configuration.
    """
    pass


class PathPlanningTrainer(EvolinoTrainer):
    """PathPlanningTrainer class

    Responsible for training the PathPlanningNetwork neural network
    for use in the surgicalsim testing environment.

    Inherits:
        EvolinoTrainer: The PyBrain built-in Evolino trainer class.
    """
    pass


if __name__ == '__main__':
    pass
