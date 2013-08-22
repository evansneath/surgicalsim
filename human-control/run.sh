#!/bin/bash

# Start the viewer in a separate process
./viewer.py &

# Start the main application loop
./run.py
