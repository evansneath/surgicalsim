#!/usr/bin/env python

from pybrain.rl.environments.ode import ODEEnvironment, actuators
import numpy as np

class HumanControlEnvironment(ODEEnvironment):
    """HumanControlEnvironment class

    A class designed to provide a interface to the ODE generated environment
    for the human data capture simulation.

    Inherits:
        ODEEnvironment

    Methods:
        set_dt: Set the time difference between steps. This also determines
            the amount of time that the torque is applied.
        set_torques: Set all 7 torques for actuation on the next step.
        step: Step the world by 'dt' seconds.
    """
    def __init__(self, xode_filename, renderer=True, realtime=True,
            ip='127.0.0.1', port='21590', buf='16384'):
        # Initialize the superclass object
        super(HumanControlEnvironment, self).__init__(
            renderer, realtime, ip, port, buf
        )

        # Load XODE file (This is generated prior to env initialization)
        self.loadXODE(xode_filename)

        # Add actuators for all joints (7)
        self.addActuator(actuators.JointActuator())

        self.dt = 0.01

        # TODO: Switch this to a 7-joint system
        self.torques = np.array([0.0, 0.0])

        return


    def set_dt(self, dt):
        """Set Time Difference

        Sets the amount of time to step the world. This can be used to adjust
        the amount of time that the set torques are applied.

        Arguments:
            dt: The difference in time to set.
        """
        self.dt = dt

        return


    def set_torques(self, torques):
        """Set Joint Torques

        Sets the joint torques to be applied at the next timestep. The joint
        array *must* contain torque values for all 7 joints in the PA10 arm.
        If no torque is applied to a joint (or a joint is not being used), set
        the torque for the joint to 0.

        Since each joint of the PA10 is a 1-axis joint, we know that each
        joint will only have one torque value.

        The order of the joints in the torques array are as follows:
            [S1, S2, S3, E1, E2, W1, W2]

        Arguments:
            torques: A list of torques to apply to the 7 joints of the PA10.
        """
        # TODO: Switch this to a 7-joint system
        assert len(torques) == 2

        self.torques = np.array(torques)

        # Set the actuators to each joint. Actuators are used in the
        # ODEEnvironments superclass
        for i, actuator in enumerate(self.actuators):
            a._update(self.torques[i])

        return


    def step(self, paused=False):
        """Step World

        Steps the world by one timestep.

        Arguments:
            paused: If True, the viewer will be updated, but the world time
                will not be incremented and no torques will be applied.
        """
        if paused:
            # Update viewer so it receives messages, but the world remains
            # unmodified
            self.updateClients()
        else:
            # Step by iterating the world by 'dt' seconds
            super(HumanControlEnvironment, self).step()

        return
