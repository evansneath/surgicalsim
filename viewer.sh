#/bin/bash

# A shell script to run the render engine and environment

PYBRAIN_DIR=~/Workspace/external/pybrain

# Start the render engine (viewer)
echo "Starting viewer"
python $PYBRAIN_DIR/pybrain/rl/environments/ode/viewer.py
