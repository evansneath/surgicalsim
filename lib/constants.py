#!/usr/bin/env python

"""Constants module

Stores all useful system constants.

Author:
    Evan Sneath - evansneath@gmail.com

License:
    Open Software License v3.0
"""

"""Path Data Format
[0] - t - normalized time value (0.0-1.0)
[1-24] - gate positions ((x,y,z) * 8)
[25-27] - tooltip position (x,y,z)
[28] - rating column (0.0-1.0)
"""

# Training Data Constants
G_TIME_IDX = 0
G_NUM_TIME_INPUTS = 1

G_GATE_IDX = G_NUM_TIME_INPUTS
G_NUM_GATE_DIMS = 3
G_NUM_GATES = 8

G_NUM_GATE_INPUTS = G_NUM_GATE_DIMS * G_NUM_GATES
G_TOTAL_NUM_INPUTS = G_NUM_TIME_INPUTS + G_NUM_GATE_INPUTS

G_POS_IDX = G_TOTAL_NUM_INPUTS
G_NUM_POS_DIMS = 3

#G_ROT_IDX = G_POS_IDX + G_NUM_POS_DIMS
#G_NUM_ROT_DIMS = 3

G_TOTAL_NUM_OUTPUTS = G_NUM_POS_DIMS# + G_NUM_ROT_DIMS

G_RATING_IDX = G_TOTAL_NUM_INPUTS + G_TOTAL_NUM_OUTPUTS
G_NUM_RATING_INPUTS = 1

G_TOTAL_NUM_MISC = G_NUM_RATING_INPUTS

G_TOTAL_COLS = G_TOTAL_NUM_INPUTS + G_TOTAL_NUM_OUTPUTS + G_TOTAL_NUM_MISC


# Long-term Training Data Constants
G_LT_INPUT_IDX = G_TIME_IDX
G_LT_NUM_INPUTS = G_NUM_TIME_INPUTS
G_LT_OUTPUT_IDX = G_POS_IDX
G_LT_NUM_OUTPUTS = G_TOTAL_NUM_OUTPUTS
