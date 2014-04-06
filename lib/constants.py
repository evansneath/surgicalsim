#!/usr/bin/env python

"""Constants module

Stores all useful system constants.

Author:
    Evan Sneath - evansneath@gmail.com

License:
    Open Software License v3.0
"""

import numpy as np
import os.path
import inspect


# ----------------------------------------------------------------------------
# Network constants

G_IP_LOCAL_DEFAULT = '127.0.0.1'
G_PORT_DEFAULT = 5555
G_CONTROLLER_MSG_FMT = '!iiddddddd'


# ----------------------------------------------------------------------------
# Environment constants

G_ENVIRONMENT_FPS = 60.0 # [Hz]
G_ENVIRONMENT_GRAVITY = 0.0 #[m/s^2]


# ----------------------------------------------------------------------------
# Mitsubishi PA10 constants

G_MAX_ACCEL = 0.8 # [m/s^2]


# ----------------------------------------------------------------------------
# End effector constants

# Tooltip constants
G_END_TOOLTIP_MASS = 10.0 # [g]
G_END_TOOLTIP_RADIUS = 0.005 # [m]

# Stick constants
G_END_STICK_MASS = 10.0 # [g]
G_END_STICK_LENGTH = 0.05 # [m]
G_END_STICK_RADIUS = 0.0025 # [m]


# ----------------------------------------------------------------------------
# Test article constants

# Table oscillation (for NeuralSim)
G_TABLE_IS_OSCILLATING = True
G_TABLE_OSCILLATION_AMP = 0.015 # [m]
G_TABLE_OSCILLATION_FREQ = 0.2 # [Hz]

# Table constants
G_TABLE_LENGTH = 0.4 # [m]
G_TABLE_HEIGHT = 0.01 # [m]

G_TABLE_Y_POS = 0.03 # [m]

G_TABLE_MASS = 100.0 # [g]

# Gate constants
G_NUM_GATES = 8

# Marker position in normalized [x, z] coordinates
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

# The y-position of the marker target top
G_GATE_HEIGHT = 0.10 # [m]

# The width between marker posts
G_GATE_WIDTH = 0.04 # [m]

# The radius of each marker post
G_GATE_POST_RADIUS = 0.005 # [m]

# The x,z-positional multiplier to the marker norms
G_GATE_POS = 0.16 # [m]

# Marker rotations
G_GATE_NORM_ROT = np.array([
    0.625,
    0.75,
    0.875,
    1.0,
    1.125,
    0.25,
    0.375,
    0.5,
])

# Randomized marker height offset limit
G_GATE_HEIGHT_RAND = 0.0 # [m]

# Randomized marker position (both x, and z) offset limit
G_GATE_POS_RAND = 0.025 # [m]

# Randomized marker rotation offset limit
G_GATE_ROT_RAND = np.deg2rad(0.0) # [rad]


# ----------------------------------------------------------------------------
# Training data constants

"""Path Data Format
[0] - t - normalized time value (0.0-1.0)
[1-32] - gate positions ((x,y,z,theta) * 8)
[33-36] - tooltip position (x,y,z)
[37] - rating column (0.0-1.0)
"""

# Used for calculating and retrieving path matrix data

# Inputs
G_TIME_IDX = 0
G_NUM_TIME_INPUTS = 1

G_GATE_IDX = G_NUM_TIME_INPUTS
G_NUM_GATE_DIMS = 4

G_NUM_GATE_INPUTS = G_NUM_GATE_DIMS * G_NUM_GATES
G_TOTAL_NUM_INPUTS = G_NUM_TIME_INPUTS + G_NUM_GATE_INPUTS

G_POS_IDX = G_TOTAL_NUM_INPUTS

# Outputs
G_NUM_POS_DIMS = 3

G_TOTAL_NUM_OUTPUTS = G_NUM_POS_DIMS

# Rating
G_RATING_IDX = G_TOTAL_NUM_INPUTS + G_TOTAL_NUM_OUTPUTS
G_NUM_RATING_INPUTS = 1

# Totals
G_TOTAL_NUM_MISC = G_NUM_RATING_INPUTS
G_TOTAL_COLS = G_TOTAL_NUM_INPUTS + G_TOTAL_NUM_OUTPUTS + G_TOTAL_NUM_MISC


# ----------------------------------------------------------------------------
# Artificial neural network constants

# NOTE: This is user-defined and should probably be changed for your needs
G_TRAINING_DATA_DIR = '/Users/evan/Workspace/surgicalsim/data'

G_RNN_XML_OUT = 'trained-rnn.xml'

G_RNN_STATIC_PATH_OUT = 'static-path.dat'
G_RNN_DYNAMIC_PATH_OUT = 'dynamic-path.dat'

# Path planning (long-term) training data constants
G_RNN_NUM_HIDDEN_NODES = 100

G_RNN_INPUT_IDX = G_TIME_IDX
G_RNN_NUM_INPUTS = G_NUM_TIME_INPUTS

G_RNN_OUTPUT_IDX = G_POS_IDX
G_RNN_NUM_OUTPUTS = G_TOTAL_NUM_OUTPUTS

G_RNN_GENERATED_TIME_STEPS = 1000 # [steps]

# Training constants
G_RNN_MAX_ITERATIONS = 30
G_RNN_CONVERGENCE_THRESHOLD = -0.00005
G_RNN_REQUIRED_CONVERGENCE_STREAK = 10
