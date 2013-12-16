#!/usr/bin/env python

"""Network module

Contains the neural network class for regression training and testing of the
surgicalsim environment.

Author:
    Evan Sneath - evansneath@gmail.com

License:
    Open Software License v3.0

Classes:
    LongTermPlanningNetwork: Recurrent LSTM neural network class for path prediction.
    LongTermPlanningTrainer: Neural network trainer for path prediction network.
    ShortTermPlanningNetwork: Recurrent neural network class for path correction.
    ShortTermPlanningTrainer: Neural network trainer for path correction network.
"""


# Import pybrain neural network modules
import numpy as np

from pybrain.supervised.evolino.networkwrapper import EvolinoNetwork
from pybrain.supervised.trainers.evolino import EvolinoTrainer

from pybrain.structure import FullConnection, RecurrentNetwork, TanhLayer, LinearLayer, BiasUnit
from pybrain.supervised import BackpropTrainer

import surgicalsim.lib.constants as constants


class LongTermPlanningNetwork(EvolinoNetwork):
    """PathPlanningNetwork class

    The primary path planning network for the surgicalsim testing environment.

    Inherits:
        EvolinoNetwork: The PyBrain built-in Evolino network configuration.
    """
    pass


class LongTermPlanningTrainer(EvolinoTrainer):
    """PathPlanningTrainer class

    Responsible for training the LongTermPlanningNetwork neural network
    for use in the surgicalsim testing environment.

    Inherits:
        EvolinoTrainer: The PyBrain built-in Evolino trainer class.
    """
    pass


class ShortTermPlanningNetwork(RecurrentNetwork):
    """ShortTermPlanningNetwork class

    The secondary path planning network for the surgicalsim testing environment.

    Inherits:
        RecurrentNetwork: The PyBrain built-in RNN configuration
    """
    def __init__(self, indim, outdim, hiddim, *args, **kwargs):
        super(ShortTermPlanningNetwork, self).__init__(*args, **kwargs)

        # Create network modules
        self._in_layer = LinearLayer(indim+outdim, name='input')
        self._hid_layer = TahnLayer(hiddim, name='hidden')
        self._out_layer = LinearLayer(outdim, name='output')
        self._bias = BiasUnit(name='bias')

        # Add modules to network
        self.addInputModule(self._in_layer)
        self.addModule(self._hid_layer)
        self.addModule(self._bias)
        self.addOutputModule(self._out_layer)

        # Add recurrent network connections
        self.addConnection(FullConnection(self['input'], self['hidden']))
        self.addConnection(FullConnection(self['bias'], self['hidden']))
        self.addRecurrentConnection(FullConnection(self['hidden'], self['hidden']))
        self.addConnection(FullConnection(self['hidden'], self['output']))

        self.sortModules()

        self.backprojection_factor = 1.0

        return

    def activate(self, input):
        backprojection = self._get_last_output()
        backprojection *= self.backprojection_factor

        full_input = self._create_full_input(input, backprojection)

        output = super(ShortTermPlanningNetwork, self).activate(full_input)

        self._set_last_output(output)

        return

    def _create_full_input(self, input, output):
        if self.indim > 0:
            return np.append(input, output)

        return np.array(output)

    def _get_last_output(self):
        if self.offset == 0:
            return np.zeros(self.outdim)

        return self.outputbuffer[self.offset - 1]

    def _set_last_output(self, output):
        self.outputbuffer[self.offset - 1][:] = output

        return


class ShortTermPlanningTrainer(BackpropTrainer):
    """ShortTermPlanningTrainer class

    Responsible for training the ShortTermPlanningNetwork neural network
    for use in the surgicalsim testing environment.

    Inherits:
        BackpropTrainer: The PyBrain built-in RNN backpropogation trainer.
    """
    pass


if __name__ == '__main__':
    pass
