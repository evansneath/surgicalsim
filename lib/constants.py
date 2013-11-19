#!/usr/bin/env python

"""Constants module

Stores all useful system constants.

Author:
    Evan Sneath - evansneath@gmail.com

License:
    Open Software License v3.0
"""


# Path Data Constants
G_TIME_COL = 0
G_POS_DIMS = 3
G_ROT_DIMS = 3

G_GATE_DIMS = G_POS_DIMS
G_NUM_GATES = 8

G_GATE_INPUTS = G_GATE_DIMS * G_NUM_GATES
G_TOTAL_INPUTS = 1 + G_GATE_INPUTS

G_TOTAL_OUTPUTS = G_POS_DIMS# + G_ROT_DIMS
