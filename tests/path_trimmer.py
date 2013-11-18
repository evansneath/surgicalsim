#!/usr/bin/env python

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

from surgicalsim.lib.datastore import retrieve, store, split_data


# The number of inputs at the start of the time sequence array
G_GATE_DIM = 3
G_NUM_GATES = 8
g_gate_inputs = G_GATE_DIM * G_NUM_GATES
g_num_inputs = 1 + g_gate_inputs

g_figure = None
g_ax = None


def display_path(ok_path, trim_path):
    """Display Path

    Plots the path to maintain and path to eliminate in an easy to read
    format.

    Arguments:
        ok_path: The time sequence array of the path to maintain.
        trim_path: The time sequence array of the path to eliminate.
    """
    global g_figure, g_ax

    if g_figure is None:
        g_figure = plt.figure()
        g_ax = g_figure.gca(projection='3d')

    g_ax.clear()
    
    g_ax.set_title('End Effector Path')
    g_ax.set_xlabel('Position X Axis [m]')
    g_ax.set_ylabel('Position Z Axis [m]')
    g_ax.set_zlabel('Position Y Axis [m]')

    g_ax.set_xlim3d((-0.3, 0.3))
    g_ax.set_ylim3d((-0.3, 0.3))
    g_ax.set_zlim3d((0.0, 0.2))

    g_ax.grid(True)

    # Transpose this data from (step X dim) to (dim X step)
    if ok_path is not None and len(ok_path) > 0:
        ok_path_in, ok_path_out = split_data(ok_path, g_num_inputs)
        g_ax.plot(ok_path_out[0], ok_path_out[1], -ok_path_out[2],
                'b-', zdir='y')

        for gate in range(G_NUM_GATES):
            start = 1 + (gate * G_GATE_DIM)
            end = start + G_GATE_DIM
            gate_pos = ok_path_in[start:end]
            g_ax.plot(gate_pos[0], gate_pos[1], -gate_pos[2], color='black',
                    marker='+', zdir='y')

    if trim_path is not None and len(trim_path) > 0:
        trim_path_in, trim_path_out = split_data(trim_path, g_num_inputs)
        g_ax.plot(trim_path_out[0], trim_path_out[1], -trim_path_out[2],
                'r--', zdir='y')

        for gate in range(G_NUM_GATES):
            start = 1 + (gate * G_GATE_DIM)
            end = start + G_GATE_DIM
            gate_pos = trim_path_in[start:end]
            g_ax.plot(gate_pos[0], gate_pos[1], -gate_pos[2], color='black',
                    marker='+', zdir='y')

    g_figure.show()
    return


def normalize_time(data, t_col=0, t_max=1.0):
    data[:, t_col] = data[:, t_col] / np.max(data[:, t_col])
    return data


def trim_path(path):
    # Show the path initially
    display_path(path, None)

    # Determine if the beginning of the path should be trimmed
    while True:
        trim = raw_input('Trim from the beginning? [y/n]: ')
        if trim.lower() == 'y' or trim.lower() == 'n':
            break
        else:
            print('Unexpected input encountered...')

    while True:
        if trim.lower() != 'y':
            break

        while True:
            trim_index = raw_input('Enter the index to trim to [0 - %d]:' %
                    (len(path)-1))
            try:
                trim_index = int(trim_index)
            except ValueError:
                print('Input could not be resolved to an integer value...')
                continue

            if 0 <= trim_index <= len(path) - 1:
                break
            else:
                print('Input index is out of range...')

        print('Displaying path...')

        display_path(path[trim_index:], path[:trim_index])

        while True:
            ok_prompt = raw_input('Does this look ok? [y/n]: ')
            if ok_prompt.lower() == 'y' or ok_prompt.lower() == 'n':
                break
            else:
                print('Unexpected input encountered...')

        if ok_prompt.lower() == 'y':
            path = path[trim_index:]
            break
        
    # Determine if the end of the path should be trimmed
    while True:
        trim = raw_input('Trim from the end? [y/n]: ')
        if trim.lower() == 'y' or trim.lower() == 'n':
            break
        else:
            print('Unexpected input encountered...')

    while True:
        if trim.lower() != 'y':
            break

        while True:
            trim_index = raw_input('Enter the index to trim from [0 - %d]:' %
                    (len(path)-1))
            try:
                trim_index = int(trim_index)
            except ValueError:
                print('Input could not be resolved to an integer value...')
                continue

            if 0 <= trim_index <= len(path) - 1:
                break
            else:
                print('Input index is out of range...')

        print('Displaying path...')

        display_path(path[:trim_index], path[trim_index:])

        while True:
            ok_prompt = raw_input('Does this look ok? [y/n]: ')
            if ok_prompt.lower() == 'y' or ok_prompt.lower() == 'n':
                break
            else:
                print('Unexpected input encountered...')

        if ok_prompt.lower() == 'y':
            path = path[:trim_index]
            break

    print('Final path...')
    display_path(path, None)

    return path


if __name__ == '__main__':
    # Get the path from a prompted filename
    in_file = raw_input('Enter path file to trim: ')
    path = retrieve(in_file)

    path = normalize_time(path)
    path = trim_path(path)

    # Store the reconstituted data
    filename = raw_input('Enter filename to save trimmed path: ')
    store(path, filename)

    exit()
