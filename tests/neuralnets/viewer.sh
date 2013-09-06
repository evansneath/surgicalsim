#/bin/bash

# A shell script to run the render engine and environment
PYBRAIN_SRC_DIR=~/Workspace/virtualenvs/surgical-sim/lib/python2.7/site-packages/pybrain

# Start the render engine (viewer)
echo "Starting viewer"
python $PYBRAIN_SRC_DIR/rl/environments/ode/viewer.py
