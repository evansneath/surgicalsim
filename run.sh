#!/bin/bash

# A shell script to run the render engine and environment

SURGICAL_SIM_DIR=~/Workspace/surgical-sim
PYBRAIN_DIR=~/Workspace/external/pybrain

# Start the render engine (viewer)
$SURGICAL_SIM_DIR/viewer.sh &

#echo "Starting viewer"
#python $PYBRAIN_DIR/pybrain/rl/environments/ode/viewer.py &

# Start the environment
echo "Starting experiment"
python $SURGICAL_SIM_DIR/start_environment.py
