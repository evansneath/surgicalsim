#!/usr/bin/env python

# Import the open dynamics engine
import ode

# Import the lagrangian generator for cross-validation of ode
#import lagrangian

# Import all pylab array and plotting tools
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def ode_dynamics(force, dt, end):
    """ODE Dynamics

    Simulates a 3-DOF system using the Open Dynamics Engine. The positional
    results of this simulation will be validated against the dynamics
    calculations for the same system.

    Arguments:
        force: The initial force applied to the center of mass of the 3rd link. [N]
        dt: The time interval between positional checks. Also the duration of
            the initially applied force. [s]
        end: The duration of the simulation. [s]

    Returns:
        A list of positional argument tuples. Tuples are in the format of
        (x, y, z) for each timestep encountered (end / dt)
    """
    results = []

    axes = {
        'x': 1,
        'y': 2,
        'z': 3,
    }

    # Generate the simulation world
    world = ode.World()

    # Use a gravity-free environment
    g = (0.0, 0.0, 0.0)
    world.setGravity(g)

    # Create link 1
    body1 = ode.Body(world)
    mass1 = ode.Mass()
    mass1.setCylinderTotal(total_mass=1.0, direction=axes['y'], r=0.001, h=1.0)
    body1.setMass(mass1)
    body1.setPosition((0.0, 0.5, 0.0))

    # Create link 2
    body2 = ode.Body(world)
    mass2 = ode.Mass()
    mass2.setCylinderTotal(total_mass=1.0, direction=axes['x'], r=0.001, h=1.0)
    body2.setMass(mass2)
    body2.setPosition((0.5, 1.0, 0.0))

    # Create link 3
    body3 = ode.Body(world)
    mass3 = ode.Mass()
    mass3.setCylinderTotal(total_mass=1.0, direction=axes['x'], r=0.001, h=1.0)
    body3.setMass(mass3)
    body3.setPosition((1.5, 1.0, 0.0))

    # Connect link 1 to the environment with a z-axis hinge joint
    joint1 = ode.HingeJoint(world)
    joint1.attach(body1, ode.environment)
    joint1.setAnchor((0.0, 0.0, 0.0))
    joint1.setAxis((0, 0, 1))

    # Connect link 2 to link 3 with a z-axis hinge joint
    joint2 = ode.HingeJoint(world)
    joint2.attach(body2, body1)
    joint2.setAnchor((0.0, 1.0, 0.0))
    joint2.setAxis((0, 0, 1))

    # Connect link 3 to link 2 with a y-axis hinge joint
    joint3 = ode.HingeJoint(world)
    joint3.attach(body2, body3)
    joint3.setAnchor((1.0, 1.0, 0.0))
    joint3.setAxis((0, 1, 0))

    # Apply the desired force for the first 'dt' seconds
    body3.addForce(force)

    current_time = 0.0

    while current_time <= end:
        # Store the positional arguments at this point in time
        pos = body3.getPosition()
        results.append(pos)

        # Move to the next timestep
        world.step(dt)
        current_time += dt

    return np.array(results)


def lagrange_dynamics(force, dt, end):
    """Lagrangian Dynamics

    Caluclates the positions of a 3-DOF system based on equations for the system.
    This 3-DOF system is identical to that defined in the ODE simulation in the
    ode_dynamics() function.

    Arguments:
        force: The initial force applied to the center of mass of the 3rd link. [N]
        dt: The time interval between positional checks. Also the duration of
            the initially applied force. [s]
        end: The duration of the simulation. [s]

    Returns:
        A list of positional argument tuples. Tuples are in the format of
        (x, y, z) for each timestep encountered (end / dt)
    """
    # Define link lengths [m]
    l_1 = 1.0
    l_2 = 1.0
    l_3 = 1.0

    # Define link masses [kg]
    m_1 = 1.0
    m_2 = 1.0
    m_3 = 1.0

    # Determine the starting angles of each joint [rad]
    theta_1 = np.pi / 2.0
    theta_2 = 0.0
    theta_3 = 0.0

    # Determine the starting angular velocities of each joint [rad/s]
    theta_dot_1 = 0.0
    theta_dot_2 = 0.0
    theta_dot_3 = 0.0

    theta_ddot_1 = 0.0
    theta_ddot_2 = 0.0
    theta_ddot_3 = 0.0

    t = np.arange(0.0, end, dt)

    # Calculate moments of initeria for each link [kg*m^2]
    # I_1 = (1.0 / 3.0) * m_1 * (l_1 ** 2)
    # I_2 = (1.0 / 3.0) * m_2 * (l_2 ** 2)
    # I_3 = (1.0 / 3.0) * m_3 * (l_3 ** 2)

    # Define kinetic energy equations for each link
    # T_1 = ((1.0 / 2.0) * m_1 * (((l_1 / 2.0) * theta_dot_1) ** 2) +
    #        ((1.0 / 2.0) * I_1 * (theta_dot_1 ** 2)))

    # T_2 = ((1.0 / 2.0) * m_2 *
    #        (((l_1 * theta_dot_2) ** 2) +
    #         (((l_2 / 2.0) * theta_dot_2) ** 2) +
    #         (l_1 * l_2 * theta_dot_1 * theta_dot_2 *
    #          np.cos(theta_2 - theta_1))) +
    #        ((1.0 / 2.0) * I_2 * (theta_dot_2 ** 2)))

    # T_3 = ((1.0 / 2.0) * m_3 *
    #        (((l_1 * theta_dot_1) ** 2) +
    #         ((l_2 * theta_dot_2) ** 2) +
    #         (((l_3 / 2.0) * theta_dot_3) ** 2) +
    #         (2.0 * l_1 * l_2 * theta_dot_1 * theta_dot_2 *
    #          np.cos(theta_2 - theta_1)) +
    #         (l_1 * l_3 * theta_dot_1 * theta_dot_3 *
    #          np.cos(theta_1) * np.sin(theta_3)) +
    #         (l_2 * l_3 * theta_dot_2 * theta_dot_3 *
    #          np.cos(theta_2) * np.sin(theta_3))) +
    #        ((1.0 / 2.0) * I_3 * (theta_dot_3 ** 2)))

    # Define equation for total kinetic energy
    # T = T_1 + T_2 + T_3

    return


def main():
    """Main Function

    Excerts forces on two equivalent dynamics models in order to validate the
    Open Dynamics Engine for a 3-DOF system.
    """
    # Determine the initial force to apply to the center of mass of the 3rd
    # link of the system. This force lasts for the first 'dt' seconds.
    force = (25.0, 25.0, 25.0) # [N]

    # Determine the amount of time for the force to be applied and the time
    # interval between positional outputs.
    dt = 0.01 # [s]

    # The total time duration of the simulation.
    end = 2.0 # [s]

    # Run ODE simulation. Gather results.
    print 'Running ODE simulation'
    ode_results = ode_dynamics(force, dt, end)

    # Run dynamics equations. Gather results.
    print 'Running lagrangian dynamics'
    lagrange_results = lagrange_dynamics(force, dt, end)

    # Split results lists into lists of [[x1, x2, ...], [y1, ...], [z1, ...]]
    # instead of the current format of a tuple for each time step
    ode_x, ode_y, ode_z = [list(t) for t in zip(*ode_results)]

    # TODO: Remove the comment once the lagrangian produces results
    eq_x, eq_y, eq_z = [np.array(t) for t in zip(*ode_results)]#*lagrange_results)]

    #for result in zip(ode_x, ode_y, ode_z):
    #    print 'x=%6.3f  y=%6.3f  z=%6.3f' % result

    print 'Plotting results'

    # Generate the 3D plots
    fig1 = plt.figure()
    fig1.suptitle('Dynamic Motion Comparison')

    # Plot the ODE simulation's data
    fig1_ax1 = fig1.add_subplot(1, 2, 1, projection='3d')
    fig1_ax1.plot(
        xs=ode_x,
        ys=ode_z,
        zs=ode_y,
    )
    fig1_ax1.set_title('ODE Simulation')
    fig1_ax1.set_xlabel('x [m]')
    fig1_ax1.set_ylabel('z [m]')
    fig1_ax1.set_zlabel('y [m]')
    fig1_ax1.axis('equal')

    # Plot the equation time data
    fig1_ax2 = fig1.add_subplot(1, 2, 2, projection='3d')
    #fig1_ax2.plot(
    #    xs=eq_x,
    #    yx=eq_z,
    #    zs=eq_y,
    #    marker='o'
    #)
    fig1_ax2.set_title('Lagrangian Dynamics')
    fig1_ax2.set_xlabel('x [m]')
    fig1_ax2.set_ylabel('z [m]')
    fig1_ax2.set_zlabel('y [m]')

    # Generate the 2D positional plots
    fig2 = plt.figure()
    fig2.suptitle('Positional Axes Comparisons')

    time_steps = np.arange(0.0, end, dt)

    # Plot the x-axis comparisons
    fig2_ax1 = fig2.add_subplot(3, 1, 1)
    fig2_ax1.plot(time_steps, ode_x, 'r--')
    fig2_ax1.set_title('X Position Comparison')
    fig2_ax1.set_xlabel('t [s]')
    fig2_ax1.set_ylabel('x [s]')

    # Plot the y-axis comparisons
    fig2_ax2 = fig2.add_subplot(3, 1, 2)
    fig2_ax2.plot(time_steps, ode_y, 'r--')
    fig2_ax2.set_title('Y Position Comparison')
    fig2_ax2.set_xlabel('t [s]')
    fig2_ax2.set_ylabel('y [s]')

    # Plot the z-axis comparisons
    fig2_ax3 = fig2.add_subplot(3, 1, 3)
    fig2_ax3.plot(time_steps, ode_y, 'r--')
    fig2_ax3.set_title('Z Position Comparison')
    fig2_ax3.set_xlabel('t [s]')
    fig2_ax3.set_ylabel('z [s]')

    # Calculate the positional errors between the two data sets
    error_x = np.absolute(ode_x - eq_x)
    error_y = np.absolute(ode_y - eq_y)
    error_z = np.absolute(ode_z - eq_z)

    # Generate the 2D error comparison plots
    fig3 = plt.figure()
    fig3.suptitle('Positional Errors')

    # Plot the x-axis errors
    fig3_ax1 = fig3.add_subplot(3, 1, 1)
    fig3_ax1.plot(time_steps, error_x, 'b-')
    fig3_ax1.set_title('X Position Error')
    fig3_ax1.set_xlabel('t [s]')
    fig3_ax1.set_ylabel('x error [m]')

    fig3_ax2 = fig3.add_subplot(3, 1, 2)
    fig3_ax2.plot(time_steps, error_y, 'b-')
    fig3_ax2.set_title('Y Position Error')
    fig3_ax2.set_xlabel('t [s]')
    fig3_ax2.set_ylabel('y error [m]')

    fig3_ax1 = fig3.add_subplot(3, 1, 3)
    fig3_ax1.plot(time_steps, error_z, 'b-')
    fig3_ax1.set_title('Z Position Error')
    fig3_ax1.set_xlabel('t [s]')
    fig3_ax1.set_ylabel('z error [m]')

    plt.show()

    print 'Done'
    return


if __name__ == '__main__':
    main()
    exit()
