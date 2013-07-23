#!/usr/bin/env python

import numpy as np


def calc_distance(source, destination):
    """Calculate Distance

    Calculates the distance between any two similar arrays.

    Arguments:
        source: The source position.
        destination: The destination position.

    Returns:
        The calculated distance between the source and destination in a
        similarly sized array as both source and destination.
    """
    return np.sqrt(((source - destination) ** 2).sum())


def pid_controller(input, k_u, t_u, e_p=None, e_i=None, e_d=None, scale=1.0):
    """PID Controller

    Implements a PID controller with tuning using the Ziegler-Nichols method.

    Arguments:

    Returns:

    """
    k_p = 0.0
    k_i = 0.0
    k_d = 0.0

    u = np.zeros_like(input)

    if e_d is not None:
        k_p = 0.60 * k_u
        k_i = 2.0 * k_p / t_u
        k_d = k_p * t_u / 8.0
    elif e_i is not None:
        k_p = 0.45 * k_u
        k_i = 1.2 * k_p * t_u

        e_d = np.zeros_like(input)
    elif e_p is not None:
        k_p = 0.5 * k_u

        e_i = np.zeros_like(input)
        e_d = np.zeros_like(input)
    else:
        e_p = np.zeros_like(input)
        e_i = np.zeros_like(input)
        e_d = np.zeros_like(input)

    p = k_p * e_p
    i = k_i * e_i
    d = k_d * e_d

    u = p + i + d

    return np.tanh(input - u) * scale
