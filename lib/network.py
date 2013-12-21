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

import numpy as np

# Import pybrain neural network and trainer modules
from pybrain.supervised.evolino.networkwrapper import EvolinoNetwork
from pybrain.supervised.trainers.evolino import EvolinoTrainer

from pybrain.structure.networks.recurrent import RecurrentNetwork
from pybrain.structure.modules.linearlayer import LinearLayer
from pybrain.structure.connections.full import FullConnection
from pybrain.structure.modules.module import Module
from pybrain.structure.modules.biasunit import BiasUnit
from pybrain.structure.modules.tanhlayer import TanhLayer
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


class ShortTermPlanningNetwork(Module):
    """ShortTermPlanningNetwork class

    The secondary path planning network for the surgicalsim testing environment.

    Inherits:
        RecurrentNetwork: The PyBrain built-in RNN configuration
    """
    def __init__(self, indim, outdim, hiddim):
        self._network = RecurrentNetwork()

        Module.__init__(self, indim, outdim)

        # Create network modules
        self._in_layer = LinearLayer(indim+outdim, name='input')
        self._hid_layer = TanhLayer(hiddim, name='hidden')
        self._out_layer = LinearLayer(outdim, name='output')
        self._bias = BiasUnit(name='bias')

        # Add modules to network
        self._network.addInputModule(self._in_layer)
        self._network.addModule(self._hid_layer)
        self._network.addModule(self._bias)
        self._network.addOutputModule(self._out_layer)

        # Create network connections
        self._in_to_hid_connection = FullConnection(self._in_layer, self._hid_layer)
        self._bias_to_hid_connection = FullConnection(self._bias, self._hid_layer)
        self._hid_to_hid_connection = FullConnection(self._hid_layer, self._hid_layer)
        self._hid_to_out_connection = FullConnection(self._hid_layer, self._out_layer)

        # Add connections to network
        self._network.addConnection(self._in_to_hid_connection)
        self._network.addConnection(self._bias_to_hid_connection)
        self._network.addRecurrentConnection(self._hid_to_hid_connection)
        self._network.addConnection(self._hid_to_out_connection)

        self._network.sortModules()

        self.backprojection_factor = 1.0

        return

    @property
    def params(self):
        return self._network.params

    @params.setter
    def params(self, val):
        self._network.params = val
        return

    @property
    def outputbuffer(self):
        return self._network.outputbuffer

    @outputbuffer.setter
    def outputbuffer(self, val):
        self._network.outputbuffer = val
        return

    @property
    def outputerror(self):
        return self._network.outputerror

    @outputerror.setter
    def outputerror(self, val):
        self._network.outputerror = val
        return

    @property
    def inputbuffer(self):
        return self._network.inputbuffer

    @inputbuffer.setter
    def inputbuffer(self, val):
        self._network.inputbuffer = val
        return

    @property
    def inputerror(self):
        return self._network.inputerror

    @inputerror.setter
    def inputerror(self, val):
        self._network.inputerror = val
        return

    @property
    def offset(self):
        return self._network.offset

    @offset.setter
    def offset(self, val):
        self._network.offset = val
        return

    @property
    def derivs(self):
        return self._network.derivs

    @derivs.setter
    def derivs(self, val):
        self._network.derivs = val
        return

    def reset(self):
        self._network.reset()
        return

    def resetDerivatives(self, *args, **kwargs):
        # Use the network's resetDerivatives function
        return self._network.resetDerivatives(*args, **kwargs)

    def activate(self, input):
        backprojection = self._get_last_output()
        backprojection *= self.backprojection_factor
        full_input = self._create_full_input(input, backprojection)

        output = self._network.activate(full_input)

        self.offset = self._network.offset
        self._set_last_output(output)

        return

    def _create_full_input(self, input, output):
        if self.indim > 0:
            return np.append(input, output)

        return np.array(output)

    def _get_last_output(self):
        if self.offset == 0:
            return np.zeros(self.outdim)

        return self._network.outputbuffer[self.offset - 1]

    def _set_last_output(self, output):
        self._out_layer.outputbuffer[self.offset - 1][:] = output

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
