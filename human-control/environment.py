#!/usr/bin/env python

import numpy as np
from pybrain.rl.environments.ode import ODEEnvironment, actuators

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
            ip='127.0.0.1', port='21590', buf='16384', gravity=0.0):
        # Initialize the superclass object
        super(HumanControlEnvironment, self).__init__(
            renderer, realtime, ip, port, buf, gravity
        )

        # Load XODE file (This is generated prior to env initialization)
        self.loadXODE(xode_filename)

        # Add actuators for all joints (7)
        self.addActuator(actuators.JointActuator())

        self.dt = 0.01

        # Create a movement group for the pointer. Note that the first body
        # defined in the group currently acts as the center of rotation. All
        # objects in the group should be fixed to at least one other object.
        self.groups = {
                'pointer': ['tooltip', 'stick'],
        }

        self.init_body_positions = {}

        # Get the initial locations for each body object. We know init velocities
        # will be zero. No forces are applied at first timestep
        for (body, _) in self.body_geom:
            if body is not None:
                self.init_body_positions[body.name] = self.get_body_pos(body.name)

        return


    def set_group_pos(self, group_name, pos):
        for body_name in self.groups[group_name]:
            new_pos = (np.array(self.init_body_positions[body_name]) +
                    np.array(pos))

            self.set_body_pos(body_name, new_pos)

        return


    def set_group_linear_vel(self, group_name, vel):
        for body_name in self.groups[group_name]:
            new_vel = np.array(vel)
            self.set_body_linear_vel(body_name, new_vel)

        return

    
    def set_group_angular_vel(self, group_name, vel):
        for body_name in self.groups[group_name]:
            new_vel = np.array(vel)

            self.set_body_angular_vel(body_name, tuple(new_vel))

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
            if body is not None and body.name == name:
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
        body.setPosition(tuple(pos))
        return


    def get_body_angular_vel(self, name):
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


    def set_body_angular_vel(self, name, vel):
        """Set Body Angular Velocity

        Sets the angular velocity of the body.

        Arguments:
            name: The name of the body to modify.
            vel: A 3-object tuple or list containing (x, y, z) velocities.

        Returns:
            None
        """
        body = self.get_body_by_name(name)
        body.setAngularVel(tuple(vel))
        return


    def get_body_linear_vel(self, name):
        """Get Body Linear Velocity

        Gets the linear velocity of the body.

        Arguments:
            name: The name of the body to find.

        Returns:
            A 3-item tuple of (x, y, z) velocities.
        """
        body = self.get_body_by_name(name)
        vel = body.getLinearVel()
        return vel


    def set_body_linear_vel(self, name, vel):
        """Set Body Linear Velocity

        Sets the linear velocity of the body.

        Arguments:
            name: The name of the body to modify.
            vel: A 3-object tuple or list containing (x, y, z) velocities.

        Returns:
            None
        """
        body = self.get_body_by_name(name)
        body.setLinearVel(tuple(vel))
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
