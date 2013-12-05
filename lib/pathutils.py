#!/usr/bin/env python

"""Path Utilities module

Contains utilties for modifying and displaying sets of path data
containing the input and output data from TrainingSim.

Author:
    Evan Sneath - evansneath@gmail.com

License:
    Open Software License v3.0

Functions:
    display_path: Displays the path and gates of a set of data.
    normalize_time: Normalizes the time column of a set of data.
    trim_path: Provides a user prompt wizard for trimming the
        start and end sets of data
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider, Button

import surgicalsim.lib.constants as constants
import surgicalsim.lib.datastore as datastore


# Global vars used only for the trim_path() function. It's not pretty, but it
# gets the job done (mangled to prevent use in external modules)
__g_start_trim_index = 0
__g_end_trim_index = 0
__g_trim_ok = False


def display_path(axis, path, trim1=None, trim2=None, title='End Effector Path'):
    """Display Path

    Plots the path to maintain and path to eliminate in an easy to read
    format.

    Arguments:
        path: The time sequence array of the path to maintain.
        trim1: The time sequence array of the path to trim. (Default: None)
        trim2: The time sequence array of the path to trim. (Default: None)
        title: The title of the plot
    """
    assert len(path) > 0

    axis.clear()
    
    axis.set_title(title)
    axis.set_xlabel('Position X Axis [m]')
    axis.set_ylabel('Position Z Axis [m]')
    axis.set_zlabel('Position Y Axis [m]')

    axis.set_xlim3d((-0.3, 0.3))
    axis.set_ylim3d((-0.3, 0.3))
    axis.set_zlim3d((0.0, 0.2))

    axis.grid(True)

    # Transpose this data from (step X dim) to (dim X step)
    path_in, path_out = datastore.split_data(path, constants.G_TOTAL_INPUTS)

    axis.plot(path_out[:,0], path_out[:,1], -path_out[:,2], 'b-', zdir='y')

    for gate in range(constants.G_NUM_GATES):
        start = 1 + (gate * constants.G_GATE_DIMS)
        end = start + constants.G_GATE_DIMS

        gate_pos = path_in[:,start:end]

        axis.plot(gate_pos[:1,0], gate_pos[:1,1], -gate_pos[:1,2], color='black',
                marker='+', zdir='y')

    if trim1 is not None and len(trim1) > 0:
        _, trim1_path = datastore.split_data(trim1,
                constants.G_TOTAL_INPUTS)

        axis.plot(trim1_path[:,0], trim1_path[:,1], -trim1_path[:,2],
                'r--', zdir='y')

    if trim2 is not None and len(trim2) > 0:
        _, trim2_path = datastore.split_data(trim2,
                constants.G_TOTAL_INPUTS)

        axis.plot(trim2_path[:,0], trim2_path[:,1], -trim2_path[:,2],
                'r--', zdir='y')

    return


def normalize_time(data, t_col=0):
    """Normalize Time

    Normalizes the timestep column to the value of t_max.

    Arguments:
        t_col: The column index of the time step data. (Default: 0)

    Returns:
        Numpy data array with the time step column normalized.
    """
    # Draw the first time step down to zero if it is non-zero
    data[:, t_col] = data[:, t_col] - np.min(data[:, t_col])

    # Normalize the time step data to a max of 1.0
    data[:, t_col] = data[:, t_col] / np.max(data[:, t_col])

    # Data now ranges between 0.0 and 1.0
    return data



def trim_path(path):
    """Trim Path

    Provides simple interface in order to trim the given path to
    a desired, trainable path.

    Arguments:
        path: The full path input/output numpy array.

    Returns:
        A trimmed path input/output numpy array.
    """
    global __g_start_trim_index
    global __g_end_trim_index
    global __g_trim_ok

    __g_start_trim_index = 0
    __g_end_trim_index = len(path) - 1

    fig = plt.figure(facecolor='white')
    axis = fig.gca(projection='3d')

    plt.subplots_adjust(bottom=0.2)

    slider_start_axis = plt.axes([0.15, 0.06, 0.6, 0.03], axisbg='w')
    slider_start = Slider(slider_start_axis, 'Start', valmin=0,
            valmax=len(path), valfmt='%d', valinit=0, closedmax=False,
            color='r')

    def start_changed(val):
        global __g_start_trim_index
        global __g_end_trim_index

        __g_start_trim_index = int(round(val))

        display_path(
            axis,
            path[__g_start_trim_index:__g_end_trim_index],
            trim1=path[:__g_start_trim_index],
            trim2=path[__g_end_trim_index:],
            title='Trim Path'
        )

        plt.draw()
        return

    slider_start.on_changed(start_changed)

    slider_end_axis = plt.axes([0.15, 0.025, 0.6, 0.03], axisbg='w')
    slider_end = Slider(slider_end_axis, 'End', valmin=0, valmax=len(path)-2,
            valfmt='%d', valinit=len(path)-1, slidermin=slider_start,
            closedmin=False, color='r')

    slider_start.slidermax = slider_end

    def end_changed(val):
        global __g_start_trim_index
        global __g_end_trim_index

        __g_end_trim_index = int(round(val))

        display_path(
            axis,
            path[__g_start_trim_index:__g_end_trim_index],
            trim1=path[:__g_start_trim_index],
            trim2=path[__g_end_trim_index:],
            title='Trim Path'
        )

        plt.draw()
        return

    slider_end.on_changed(end_changed)

    button_ok_axis = plt.axes([0.82, 0.02, 0.13, 0.08])
    button_ok = Button(button_ok_axis, label='Trim', color='lightgrey')

    def button_clicked(event):
        global __g_trim_ok
        __g_trim_ok = True
        plt.close()
        return

    button_ok.on_clicked(button_clicked)

    # Show the path initially
    display_path(axis, path, title='Trim Path')

    plt.show()

    if __g_trim_ok:
        path = path[__g_start_trim_index:__g_end_trim_index]

    return path


if __name__ == '__main__':
    """Main

    If the module is directly called, the given file will be converted to
    a path dataset and plotted.

    Usage:
        ./path_trimmer.py <path_filename>
    """
    import sys

    if len(sys.argv) > 1:
        # Get the path from the incoming cmd line arg
        in_file = sys.argv[1]
    else:
        # Get the path from a prompted filename
        in_file = raw_input('Enter path file to trim: ')

    path = datastore.retrieve(in_file)

    # Plot the inputted path
    fig = plt.figure(facecolor='white')
    axis = fig.gca(projection='3d')

    display_path(axis, path, title='Training Path')

    plt.show()

    exit()
