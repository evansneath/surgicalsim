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


def pid_controller(input, k_u, t_u, e_p, e_i, e_d, scale=1.0):
    """PID Controller

    Implements a PID controller with tuning using the Ziegler-Nichols method.
    Note that this function can accept scalars as well as numpy arrays. All
    elements (P, I, and D) must be present to function properly. If an element
    is usused, an array of zeros with similar size to input must be set as the
    argument.

    Arguments:
        input: The input control to the system (numpy array acceptable)
        k_u:
        t_u:
        e_p:
        e_i:
        e_d:
        scale: The value to scale the output value(s) between. (Default: 1.0)

    Returns:
        A PID regulated value to feed back to the system.
    """
    # Ensure that all input arrays are of proper size
    assert np.shape(input) == np.shape(e_p) == np.shape(e_i) == np.shape(e_d)

    k_p = 0.60 * k_u
    k_i = 2.0 * k_p / t_u
    k_d = k_p * t_u / 8.0

    k_p = 1.0
    k_i = 0.9
    k_d = 0.9

    p = k_p * e_p
    i = k_i * e_i
    d = k_d * e_d

    u = p + i + d

    normalized_output = np.tanh(input - u)
    scaled_output = normalized_output * scale

    return scaled_output
