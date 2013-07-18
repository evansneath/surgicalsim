#!/usr/bin/env python

import ode
import scipy

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
    mass1.setCylinderTotal(total_mass=1.0, direction=axes['y'], r=0.1, h=1.0)
    body1.setMass(mass1)
    body1.setPosition((0.0, 0.5, 0.0))

    # Create link 2
    body2 = ode.Body(world)
    mass2 = ode.Mass()
    mass2.setCylinderTotal(total_mass=1.0, direction=axes['x'], r=0.1, h=1.0)
    body2.setMass(mass2)
    body2.setPosition((0.5, 1.0, 0.0))

    # Create link 3
    body3 = ode.Body(world)
    mass3 = ode.Mass()
    mass3.setCylinderTotal(total_mass=1.0, direction=axes['x'], r=0.1, h=1.0)
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
        x, y, z = body3.getPosition()
        u, v, w = body3.getLinearVel()

        # Store the positional arguments at this point in time
        results.append((x, y, z))

        world.step(dt)
        current_time += dt

    return results


def equation_dynamics(force, dt, end):
    """Equation Dynamics

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
    return


def main():
    """Main Function

    Excerts forces on two equivalent dynamics models in order to validate the
    Open Dynamics Engine for a 3-DOF system.
    """
    # Determine the initial force to apply to the center of mass of the 3rd
    # link of the system. This force lasts for the first 'dt' seconds.
    force = (25.0, 25.0, 35.0) # [N]

    # Determine the amount of time for the force to be applied and the time
    # interval between positional outputs.
    dt = 0.01 # [s]

    # The total time duration of the simulation.
    end = 2.0 # [s]

    # Run ODE simulation. Gather results.
    ode_results = ode_dynamics(force, dt, end)

    # Run dynamics equations. Gather results.
    equation_results = equation_dynamics(force, dt, end)

    # Split results lists into lists of [[x1, x2, ...], [y1, ...], [z1, ...]]
    # instead of the current format of a tuple for each time step
    ode_results_split = [list(t) for t in zip(*ode_results)]
    #equation_results_split = [list(t) for t in zip(*equation_results)]
    
    for result in ode_results:
        print 'x=%6.3f  y=%6.3f  z=%6.3f' % result

    # Plot the ODE simulation's data
    figure1 = plt.figure()
    ax1 = figure1.add_subplot(121, projection='3d')
    ax1.scatter(
        xs=ode_results_split[0],
        ys=ode_results_split[2],
        zs=ode_results_split[1],
        marker='o'
    )
    ax1.set_xlabel('x [m]')
    ax1.set_ylabel('z [m]')
    ax1.set_zlabel('y [m]')

    ax2 = figure1.add_subplot(122, projection='3d')

    plt.show()

    return


if __name__ == '__main__':
    main()
    exit()
