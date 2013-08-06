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

        # TODO: Switch this to a 7-body system
        self.velocities = np.array([0.0, 0.0])

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


    def increment_body_pos(self, body_name, inc_val):
        """Increment Body Position

        Increments the position of a body in the next time step by a given
        amount.

        Arguments:
            body_name: The name of the body to modify.
            inc_value: The distance to increment the body for each timestep.

        Returns:
            True if body is found, False otherwise.
        """
        direction = np.array([1, 0, 0])
        cur_pos = self.get_body_pos(body_name)

        if cur_pos is None:
            return False

        new_pos = cur_pos + (inc_val * direction)
        self.set_body_pos(body_name, new_pos)

        return True


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


    def get_body_by_name(self, name):
        """Get Body By Name

        Get a ODE body object by its name and return the original
        ODE object.

        Arguments:
            name: The name of the body to find.

        Return:
            The copied body object if found, None otherwise.
        """
        # Pull out the body in the (body, geom) tuple
        for body, _ in self.body_geom:
            if body.name == name:
                return body

        return None


    def get_body_pos(self, name):
        """Get Body Position

        Gets the current position of a given body.

        Arguments:
            name: The name of the body to find.

        Returns:
            A 3-item tuple containing (x, y, z) positional coordinates.
        """
        body = self.get_body_by_name(name)
        pos = body.getPosition()
        return pos


    def set_body_pos(self, name, pos):
        """Set Body Position

        Sets the body position for the next timestep.

        Arguments:
            name: The name of the body to modify.
            pos: The new position of the body in the form of a 3-item tuple.

        Returns:
            None
        """
        body = self.get_body_by_name(name)
        body.setPosition(pos)
        return


    def get_body_ang_vel(self, name):
        """Get Body Angular Velocity

        Gets the angular velocity of the body.

        Arguments:
            name: The name of the body to find.

        Returns:
            A 3-item tuple of (x, y, z) velocities.
        """
        body = self.get_body_by_name(name)
        vel = body.getAngularVel()
        return vel


    def set_body_ang_vel(self, name, vel):
        """Set Body Angular Velocity

        Sets the angular velocity of the body.

        Arguments:
            name: The name of the body to modify.
            vel: A 3-object tuple or list containing (x, y, z) velocities.

        Returns:
            None
        """
        body = self.get_body_by_name(name)
        body.setAngularVel(vel)
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
