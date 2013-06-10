#!/usr/bin/env python

from pa10_xode import XODEPA10
from pa10_env import PA10Environment

import os.path

def start_environment():
    # Generate the xode file for world creation
    xode_name = 'pa10'

    if os.path.exists('./'+xode_name+'.xode'):
        os.remove('./'+xode_name+'.xode')

    xode = XODEPA10(xode_name)
    xode.writeXODE('./'+xode_name)

    # Create the environment
    env = PA10Environment(xodeFile='./'+xode_name+'.xode')

    # Loop in this simulation forever
    while True:
        env.step()
        if env.stepCounter == 1000:
            #env.reset()
            pass

    return

if __name__ == '__main__':
    start_environment()
    exit()
