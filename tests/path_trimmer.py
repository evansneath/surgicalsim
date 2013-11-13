#!/usr/bin/env python

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

from surgicalsim.lib.datastore import store, files_to_dataset, list_to_dataset


def get_file_dataset():
    """Get File Dataset

    Prompts for a path input to convert and converts that raw file data to
    a SequentialDataSet class object.

    Returns:
        A SequentialDataSet class object from the given filename.
    """
    filename = raw_input('Enter path file to trim: ')

    path_dataset = files_to_dataset([filename])

    return path_dataset
    

def display_path(ok_path, trim_path):
    """Display Path
    """
    plt.ion()
    plt.figure(1)
    plt.subplot(111, aspect='equal', autoscale_on=True, projection='3d')
    plt.cla()
    
    plt.title('End Effector Path')
    plt.xlabel('Position X Axis [m]')
    plt.ylabel('Position Z Axis [m]')
    plt.zlabel('Position Y Axis [m]')
    plt.grid(True)

    if ok_path:
        plt.plot(ok_path[0], -ok_path[2], ok_path[1], 'b-')

    if trimmed_path:
        plt.plot(trim_path[0], -trim_path[2], trim_path[1], 'r--')

    plt.draw()

    return


def main():
    # Get the path from a prompted filename
    path_dataset = get_file_dataset()

    path_input = np.array(path_dataset.getField('input'))
    path = np.array(path_dataset.getField('target'))

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
        if trim.lower() == 'y':
            break

        while True:
            trim_index = raw_input('Enter the index to trim to [0 - %d]:' %
                    (len(path)-1))
            try:
                trim_index = int(trim_index)
            except ValueError:
                print('Input could not be resolved to an integer value...')
                continue

            if 0 < trim_index < len(path) - 1:
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
            path_input = path_input[trim_index:]
            break
        
    # Determine if the end of the path should be trimmed
    while True:
        trim = raw_input('Trim from the end? [y/n]: ')
        if trim.lower() == 'y' or trim.lower() == 'n':
            break
        else:
            print('Unexpected input encountered...')

    while True:
        if trim.lower() == 'y':
            break

        while True:
            trim_index = raw_input('Enter the index to trim from [0 - %d]:' %
                    (len(path)-1))
            try:
                trim_index = int(trim_index)
            except ValueError:
                print('Input could not be resolved to an integer value...')
                continue

            if 0 < trim_index < len(path) - 1:
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
            path_input = path_input[:trim_index]
            break

    print('Final path...')
    display_path(path, None)

    # Store the reconstituted data
    filename = raw_input('Enter filename to save trimmed path: ')

    trimmed_dataset = list_to_dataset(path_input, path)
    store(trimmed_dataset, filename)
    
    return


if __name__ == '__main__':
    main()
    exit()
