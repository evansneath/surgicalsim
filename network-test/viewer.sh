#/bin/bash

# A shell script to run the render engine and environment
PYBRAIN_SRC_DIR=~/Workspace/virtualenvs/surgical-sim/lib/python2.6/site-packages/PyBrain-0.3.1-py2.6.egg/

# Start the render engine (viewer)
echo "Starting viewer"
python $PYBRAIN_SRC_DIR/pybrain/rl/environments/ode/viewer.py
