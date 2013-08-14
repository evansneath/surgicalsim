#!/usr/bin/env python

__author__ = 'Evan Sneath, evansneath@gmail.com'

"""
Code modified from PyBrain CCRLGlas example model.
"""

from pybrain.rl.environments.ode import ODEEnvironment, sensors, actuators

import numpy as np


class Pa10Environment(ODEEnvironment):
    def __init__(self, xodeFile="./pa10.xode", renderer=True, realtime=True, ip="127.0.0.1", port="21590", buf='16384'):
        ODEEnvironment.__init__(self, renderer, realtime, ip, port, buf)

        # Load model file
        self.loadXODE(xodeFile)

        # Set the gravity to 0. The network can learn much easier without the
        # force of gravity to counteract
        gravity = 0.0
        self.setGravity(gravity)

        # Environment coefficient of friction
        self.FricMu = 8.0

        # Real-world time for each time step
        self.dt = 0.005

        # Number of steps time steps to simulate for each call to performAction()
        self.stepsPerAction = 1

        # Add PA10 sensors
        self.addSensor(sensors.JointSensor())
        self.addSensor(sensors.JointVelocitySensor())
        self.addSensor(sensors.SpecificBodyPositionSensor(['pa10_t2'], 'tooltipPos'))

        # Add PA10 actuators
        self.addActuator(actuators.JointActuator())

        # Reset number of actuators and sensors (observers)
        self.actLen = self.indim
        self.obsLen = self.outdim

        return


if __name__ == '__main__' :
    env = Pa10Environment()

    # Simulate this environment until the end of time
    while True:
        env.step()
