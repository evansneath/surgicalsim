#!/usr/bin/env python

"""Environment module

Defines the environment for the Surgical Sim test article simulation.

Author:
    Evan Sneath

License:
    Open Software License v3.0

Classes:
    EnvironmentInteface: Defines the Open Dynamics Engine environment for
        the surgical simulation applications given the XODE model filename.
"""

import numpy as np
import ode
from pybrain.rl.environments.ode import ODEEnvironment, actuators


class EnvironmentInterface(ODEEnvironment):
    """EnvironmentInterface class

    A class designed to provide a interface to the ODE generated environment
    for the human data capture simulation and neural network training.

    Inherits:
        ODEEnvironment: The PyBrain ODE environment class.

    Attributes:
        groups: A dictionary of group names where each value is a list of
            body names associated with that group.

    Methods:
        set_dt: Set the time difference between steps. This also determines
            the amount of time that the torque is applied.
        set_torques: Set the torques applied to actuators for one time step.
        set_group_pos: Sets the position of a group of bodies.
        set_group_linear_vel: Sets the linear velocity of a group of bodies.
        set_group_angular_vel: Sets the angular velocity of a group of bodies.
        get_body_by_name: Returns the ODE body object given a body name.
        get_body_pos: Returns the position of a body given a body name.
        set_body_pos: Sets the position of a body given a body name.
        get_body_linear_vel: Returns the velocity of a body given a body name.
        set_body_linear_vel: Sets the velocity of a body given a body name.
        get_body_angular_vel: Returns the angular velocity of a body given a
            body name.
        set_body_angular_vel: Sets the angular velocity of a body given a
            body name.
        get_joint_by_name: Returns the ODE joint object given a joint name.
        step: Step the world by 'dt' seconds.
    """
    def __init__(self, xode_filename, render=True, realtime=True,
            ip='127.0.0.1', port='21590', buffer='16384', verbose=False,
            gravity=-9.81):
        """Initialize

        Initializes the ODE world, variables, the frame rate and the 
        callback functions.

        Arguments:
            render: Determines if object information should be sent over UDP
                to the viewer client. (Boolean - Default: True)
            realtime: Determines if the simulation should have real-time
                constraints. (Boolean - Default: True)
            ip: The IP address of the viewer client. This is only used if
                render is set to True. (String - Default: '127.0.0.1')
            port: The port of the viewer client. This is only used if
                render is set to True. (String - Default: '21590')
            buf: The size of the UDP buffer. This is only used if render is
                set to True. (String - Default: '16384')
            verbose: Determines if extra debug information should be
                displayed. (Boolean - Default: False)
            gravity: The gravity in meters per second to be excerted on objects
                in the world. (Float - Default: -9.81)
        """
        # Initialize the superclass object
        super(EnvironmentInterface, self).__init__(
                render=render,
                realtime=realtime,
                ip=ip,
                port=port,
                buf=buffer,
                gravity=gravity,
                verbose=verbose
        )

        # Load XODE file (This is generated prior to env initialization)
        self.loadXODE(xode_filename)

        self.dt = 0.01

        self.get_init_body_positions()

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

    def get_init_body_positions(self):
        self.init_body_positions = {}

        # Get the initial locations for each body object. We know init velocities
        # will be zero. No forces are applied at first timestep
        for (body, _) in self.body_geom:
            if body is not None:
                self.init_body_positions[body.name] = self.get_body_pos(body.name)

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
        assert len(torques) == 7

        self.torques = np.array(torques)

        # Set the actuators to each joint. Actuators are used in the
        # ODEEnvironment superclass
        for i, actuator in enumerate(self.actuators):
            a._update(self.torques[i])

        return

    def set_group_pos(self, group_name, pos):
        """Set Group Position

        Sets the position of the body group given a group name. Note that is
        much better in the Open Dynamics Engine to move bodies using velocites.

        Arguments:
            group_name: The string value name of the group.
            pos: The 3-element array [x, y, z] of the new position for the
                group in [m].
        """
        for body_name in self.groups[group_name]:
            new_pos = (np.array(self.init_body_positions[body_name]) +
                    np.array(pos))

            self.set_body_pos(body_name, new_pos)

        return

    def set_group_linear_vel(self, group_name, vel):
        """Set Group Linear Velocity

        Sets the linear velocity of the body group given a group name.

        Arguments:
            group_name: The string value name of the group.
            vel: The 3-element array [x, y, z] of the new linear velocity
                for the group in [m/s].
        """
        for body_name in self.groups[group_name]:
            new_vel = np.array(vel)
            self.set_body_linear_vel(body_name, new_vel)

        return

    def set_group_angular_vel(self, group_name, vel):
        """Set Group Angular Velocity

        Sets the angular velocity  of the body group given a group name.

        Arguments:
            group_name: The string value name of the group.
            vel: The 3-element array [x, y, z] of the new angular velocity
                for the group in [rad/s].
        """
        for body_name in self.groups[group_name]:
            new_vel = np.array(vel)

            self.set_body_angular_vel(body_name, tuple(new_vel))

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

        return

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

    def get_joint_by_name(self, name):
        """Get Joint By Name

        Finds and returns the ODE joint object given a valid joint name.

        Arguments:
            name: The name of the joint to return.

        Returns:
            The copied joint object if found, None otherwise.
        """
        for actuator in self.actuators:
            if actuator.name == name:
                return actuator._joints[0]

        return

    #def set_motor_axis(self, name, axes):
    #    joint = self.get_joint_by_name(name)
    #    # Only 1 axis will be controlled by this motor
    #    joint.setNumAxes(1)
    #    # Set the axis (axes vector is relative to global coordinates
    #    joint.setAxis(0, 1, axes)
    #    # Set the motor control to euler rotation
    #    joint.setMode(ode.AMotorEuler)
    #    # Zero out the joint angle at this position
    #    joint.setAngle(0.0)
    #    return

    def set_motor_angular_vel(self, name, vel):
        """Set Motor Velocity

        Sets the euler rotational velocity of the motor in yaw-pitch-roll
        coordinates relative to the link 1 of the motor.

        Arguments:
            name: The name of the joint to modify.
            vel: A 1-dimensional angular velocity given in radians per second.

        Returns:
            None
        """
        joint = self.get_joint_by_name(name)
        joint.setParam(ode.ParamVel, vel)
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
            super(EnvironmentInterface, self).step()

        return


if __name__ == '__main__':
    pass
