#!/usr/bin/env python

"""World module

Contains the classes necessary for XODE file generation specific to the
Surgical Sim neural network simulation.

Author:
    Evan Sneath - evansneath@gmail.com

License:
    Open Software License v3.0

Classes:
    NeuralSimWorld: Builds all objects used for the PA10 neural net simulation.
"""

# Import numpy
import numpy as np

# Import PyBrain XODE parsing module
from pybrain.rl.environments.ode.tools.xodetools import XODEfile

# Import surgicalsim model modules
import surgicalsim.lib.models as models


class NeuralSimWorld(XODEfile):
    """NeuralSimWorld class

    Generates the XODE file used for the ODE environment.

    Inherits:
        XODEfile: An xode file building class.

    Methods:
        generate: Generates the xode model of the world.
    """
    def __init__(self, name, randomize_test_article=False):
        """Initialize

        Creates a new TrainingSimWorld object.

        Arguments:
            randomize_test_article: Determines if the test article to be
                generated will have randomized gates. (Default: False)
        """
        super(NeuralSimWorld, self).__init__(name)

        self._name = name
        self._randomize_test_article = randomize_test_article

        return

    def generate(self):
        """Generate

        Generates the xode model of the world.
        """
        self.insertFloor(y=0.0)

        # Build the test article with gates
        y_top_table = models.build_test_article(self,
                self._randomize_test_article)

        # Build the Mitsubishi PA10 robotic arm
        models.build_pa10(self, 0.0, 1.0)

        self.writeXODE('./'+self._name)

        return


if __name__ == '__main__':
    pass
