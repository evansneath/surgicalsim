#!/usr/bin/env python

"""Constants module

Stores all useful system constants.

Author:
    Evan Sneath - evansneath@gmail.com

License:
    Open Software License v3.0
"""
import numpy as np

# Gate Orientation Constants
G_NUM_GATES = 8

# Position in [x, z] coordinates
G_GATE_NORM_POS = np.array([
    [ 1,  1],
    [ 0,  1],
    [-1,  1],
    [-1,  0],
    [-1, -1],
    [ 0, -1],
    [ 1, -1],
    [ 1,  0],
])

# Rotation counter-clockwise from 'x' axis
G_GATE_NORM_ROT = np.array([
    0.375,
    0.5,
    0.625,
    0.75,
    0.875,
    0.0,
    0.125,
    0.25,
])

# Neural network constants
G_NUM_HIDDEN_NODES = 100


"""Path Data Format
[0] - t - normalized time value (0.0-1.0)
[1-32] - gate positions ((x,y,z,theta) * 8)
[33-36] - tooltip position (x,y,z)
[37] - rating column (0.0-1.0)
"""

# Training Data Constants
G_TIME_IDX = 0
G_NUM_TIME_INPUTS = 1

G_GATE_IDX = G_NUM_TIME_INPUTS
G_NUM_GATE_DIMS = 4

G_NUM_GATE_INPUTS = G_NUM_GATE_DIMS * G_NUM_GATES
G_TOTAL_NUM_INPUTS = G_NUM_TIME_INPUTS + G_NUM_GATE_INPUTS

G_POS_IDX = G_TOTAL_NUM_INPUTS
G_NUM_POS_DIMS = 3

G_TOTAL_NUM_OUTPUTS = G_NUM_POS_DIMS

G_RATING_IDX = G_TOTAL_NUM_INPUTS + G_TOTAL_NUM_OUTPUTS
G_NUM_RATING_INPUTS = 1

G_TOTAL_NUM_MISC = G_NUM_RATING_INPUTS

G_TOTAL_COLS = G_TOTAL_NUM_INPUTS + G_TOTAL_NUM_OUTPUTS + G_TOTAL_NUM_MISC


# Long-term Training Data Constants
G_LT_INPUT_IDX = G_TIME_IDX
G_LT_NUM_INPUTS = G_NUM_TIME_INPUTS
G_LT_OUTPUT_IDX = G_POS_IDX
G_LT_NUM_OUTPUTS = G_TOTAL_NUM_OUTPUTS


# Short-term Training Data Constants
G_ST_INPUT_IDX = G_GATE_IDX
G_ST_NUM_INPUTS = G_NUM_GATE_DIMS
G_ST_OUTPUT_IDX = G_POS_IDX
G_ST_NUM_OUTPUTS = G_TOTAL_NUM_OUTPUTS
