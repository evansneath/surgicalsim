#!/usr/bin/env python

from environment import HumanCaptureEnvironment
from viewer import HumanCaptureViewer
from controller import HumanCaptureController


def run():
    step_count = 0
    stop_signal = False

    env = None
    viewer = None
    omni = None

    raw_data = []

    (env, viewer, omni) = init()

    while not stop_signal:
        angles, velocities = step()
        raw_data.append((angles, velocities))

    return


def init():
    """Initialize Capture

    Creates the environment, viewer, and (Phantom Omni) controller objects
    required to run the human data capture simulation.

    Returns:
        (env, viewer, omni) - The three class objects used to run the
        simulation for human data capture.
    """
    # Start environment
    env = HumanCaptureEnvironment()

    # Start viewer
    viewer = HumanCaptureViewer()

    # Start controller
    omni = HumanCaptureController()

    return (env, viewer, omni)


def step():
    # Get change of position/velocity of controller (controller)
    # Use inverse kinematics to get joint torques (kinematics)
    # Apply torques to joints (env)
    # Update viewer (viewer)
    # Store joint angles/velocities as raw data (env -> file)
    # Check for stop signal?
    return


if __name__ == '__main__':
    run()
    exit()
