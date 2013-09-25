#!/bin/bash

# A shell script to run the render engine and environment

SURGICAL_SIM_DIR=~/Workspace/surgicalsim/tests/neuralnets

# Start the render engine (viewer)
$SURGICAL_SIM_DIR/viewer.sh &

# Start the environment
echo "Starting experiment"
python $SURGICAL_SIM_DIR/start_environment.py
