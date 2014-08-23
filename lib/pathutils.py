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
    zero_time: Zeroes the time wrt the minimum time value.
    normalize_time: Normalizes the time column of a set of data.
    trim_path: Provides a user prompt wizard for trimming the start and end
        sets of data.
    list_data_files: Provides a list of all .dat files present in a given
        directory.
    fix_starting_pos: Snaps the starting path position to the first marker.
    get_path_time: Return the time at a specific time step index.
    set_path_time: Sets the time at a specific time step index.
    get_path_tooltip_pos: Return the tooltip position at a specific time step.
    set_path_tooltip_pos: Sets the tooltip position at a specific time step.
    get_path_gate_pos: Return the position of a gate at a specific time step.
    set_path_gate_pos: Sets the position of a gate at a specific time step.
    split_segments: Returns a list of segment end-points given a full path.
    rate_segments: Prompts for segment ratings and plots segments.
"""

import os

import numpy as np
import matplotlib.pyplot as plt

from scipy.spatial.distance import cdist
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider, Button

import surgicalsim.lib.constants as constants
import surgicalsim.lib.datastore as datastore


# Global vars used only for the trim_path() function. It's not pretty, but it
# gets the job done (mangled to prevent use in external modules)
__g_start_trim_index = 0
__g_end_trim_index = 0
__g_trim_ok = False


def display_path(axis, path, dotted_paths=[], title='End Effector Path', label_axes=True, two_dimensional=False):
    """Display Path

    Plots the path to maintain and path to eliminate in an easy to read
    format.

    Arguments:
        path: The time sequence array of the path to maintain.
        dotted_paths: A list of time sequence arrays to display in dotted red.
            (Default: [])
        title: The title of the plot. (Default: 'End Effector Path')
    """
    assert len(path) > 0

    axis.clear()
    
    if title:
        axis.set_title(title, fontsize=25)

    if label_axes:
        axis.set_xlabel('Position X Axis [m]', fontsize=20)
        axis.set_ylabel('Position Z Axis [m]', fontsize=20)

        if not two_dimensional:
            axis.set_zlabel('Position Y Axis [m]', fontsize=20)

    if not two_dimensional:
        axis.set_xlim3d((-0.3, 0.3))
        axis.set_ylim3d((-0.3, 0.3))
        axis.set_zlim3d((0.0, 0.2))

    axis.grid(True)

    # Split the data into more managable input and output arrays
    path_in, path_out = datastore.split_data(path, constants.G_TOTAL_NUM_INPUTS)

    # Print the main tooltip path

    if not two_dimensional:
        axis.plot(path_out[:,0], path_out[:,1], -path_out[:,2], 'b-', zdir='y')
    else:
        axis.plot(path_out[:,0], -path_out[:,2], 'b-')

    # Print the starting gate positions
    for gate in range(constants.G_NUM_GATES):
        start = constants.G_GATE_IDX + (gate * constants.G_NUM_GATE_DIMS)
        end = start + constants.G_NUM_POS_DIMS

        gate_pos = path_in[0,start:end]

        if not two_dimensional:
            axis.plot([gate_pos[0]], [gate_pos[1]], [-gate_pos[2]], color='black',
                    marker='o', zdir='y', markersize=5)
        else:
            axis.plot([gate_pos[0]], [-gate_pos[2]], color='black',
                    marker='o', markersize=5)

    # Print the gate positions at point of closest approach
    segments = _detect_segments(path)
    for seg_idx, seg_end in enumerate(segments):
        start = constants.G_GATE_IDX + (seg_idx * constants.G_NUM_GATE_DIMS)
        end = start + constants.G_NUM_POS_DIMS

        gate_pos = path_in[seg_end,start:end] 

        if not two_dimensional:
            axis.plot([gate_pos[0]], [gate_pos[1]], [-gate_pos[2]], color='red',
                    marker='o', zdir='y', markersize=5)
        else:
            axis.plot([gate_pos[0]], [-gate_pos[2]], color='red',
                    marker='o', markersize=5)


    # Print any other paths
    for dotted_path in dotted_paths:
        if dotted_path is None or len(dotted_path) == 0:
            continue

        _, dotted_path_out = datastore.split_data(dotted_path,
                constants.G_TOTAL_NUM_INPUTS)

        if not two_dimensional:
            axis.plot(dotted_path_out[:,0], dotted_path_out[:,1], -dotted_path_out[:,2],
                    'r--', zdir='y')
        else:
            axis.plot(dotted_path_out[:,0], -dotted_path_out[:,2],
                    'r--', zdir='y')
       
    return


def zero_time(data, t_col=0):
    """Zero Time

    Reduces all time column elements by the minimum value, bringing the
    minimum to zero.

    Arguments:
        t_col: The column index of the time step data. (Default: 0)

    Returns:
        Numpy data array with the time step column zeroed.
    """
    # Draw the first time step down to zero if it is non-zero
    data[:, t_col] = data[:, t_col] - np.min(data[:, t_col])

    return data


def normalize_time(data, t_col=0):
    """Normalize Time

    Normalizes the timestep column to the value of t_max.

    Arguments:
        t_col: The column index of the time step data. (Default: 0)

    Returns:
        Numpy data array with the time step column normalized.
    """
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
            dotted_paths=[path[:__g_start_trim_index], path[__g_end_trim_index:]],
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
            dotted_paths=[path[:__g_start_trim_index], path[__g_end_trim_index:]],
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


def list_data_files(dir):
    """List Data Files

    Given a directory, find all .dat files and return the list.

    Arguments:
        dir: A string denoting a directory to search.

    Returns:
        A list of all .dat files present in that directory
    """
    dat_files = []
    for file in os.listdir(dir):
        if (os.path.isfile(os.path.join(dir, file)) and
                file.split('.')[-1] == 'dat'):
            dat_files.append(os.path.join(dir, file))

    return dat_files


def _detect_segments(data):
    """Detect Segments

    Using the minimum point from the gate, this function provides a simple way
    to break the path into segments without manual segment selection. Note that
    in practice, segments will be manually determined for rating.

    Arguments:
        data: The path data from TrainingSim.

    Returns:
        A list of segment end indices for each gate.
    """

    segment_ends = []

    # Detect a segment for each gate
    for cur_gate in xrange(constants.G_NUM_GATES):
        # The last segment should contain the end at the last index
        if cur_gate == constants.G_NUM_GATES - 1:
            segment_ends.append(data.shape[0]-1)
            continue

        cur_gate_pos_start = (constants.G_GATE_IDX +
                (cur_gate * constants.G_NUM_GATE_DIMS))
        cur_gate_pos_end = cur_gate_pos_start + constants.G_NUM_GATE_DIMS - 1

        # Calculate distance
        dist = cdist(
            data[:,constants.G_POS_IDX:constants.G_POS_IDX+constants.G_NUM_POS_DIMS],
            data[:,cur_gate_pos_start:cur_gate_pos_end],
            metric='euclidean'
        )[:,0]

        # Find the minimum distance
        closest_epoch = np.argmin(dist, axis=0)

        # Add the closest point to a list
        segment_ends.append(closest_epoch)

    return segment_ends


def fix_starting_pos(data):
    """Fix Starting Path Position

    Given a path, the starting position (data[0]) of the tooltip will be
    corrected such that the starting position is equal to the starting gate
    position. This allows for a uniform starting state for every trained path.

    Arguments:
        data: The path data from TrainingSim.
        
    Returns:
        The corrected path data.
    """
    # Get starting gate position
    gate_pos = get_path_gate_pos(data, 0, constants.G_NUM_GATES-1)

    # Calculate tooltip indices
    tt_pos_start_idx = constants.G_POS_IDX
    tt_pos_end_idx = tt_pos_start_idx + constants.G_NUM_POS_DIMS

    # Set starting tooltip position to first gate position
    data[0,tt_pos_start_idx:tt_pos_end_idx] = gate_pos

    return data


def get_path_time(path, path_idx):
    """Get Time
    """
    t_idx = constants.G_TIME_IDX
    t = path[path_idx, t_idx]

    return t


def set_path_time(path, path_idx, t):
    """Set Time
    """
    t_idx = constants.G_TIME_IDX
    path[path_idx, t_idx] = t

    return


def get_path_tooltip_pos(path, path_idx):
    """Get Tooltip Position
    """
    tooltip_pos_start_idx = constants.G_POS_IDX
    tooltip_pos_end_idx = tooltip_pos_start_idx + constants.G_NUM_POS_DIMS

    tooltip_pos = path[path_idx, tooltip_pos_start_idx:tooltip_pos_end_idx]

    return tooltip_pos


def set_path_tooltip_pos(path, path_idx, pos):
    """Set Tooltip Position
    """
    tooltip_pos_start_idx = constants.G_POS_IDX
    tooltip_pos_end_idx = tooltip_pos_start_idx + constants.G_NUM_POS_DIMS

    path[path_idx, tooltip_pos_start_idx:tooltip_pos_end_idx] = pos

    return


def get_path_gate_pos(path, path_idx, seg_idx):
    """Get Gate Position
    """
    # Determine start and end indexes of the position of current gate
    gate_pos_start_idx = (constants.G_GATE_IDX + (seg_idx
                          * constants.G_NUM_GATE_DIMS))
    gate_pos_end_idx = gate_pos_start_idx + constants.G_NUM_POS_DIMS

    # Get starting gate position
    gate_pos = path[path_idx, gate_pos_start_idx:gate_pos_end_idx]

    return gate_pos


def set_path_gate_pos(path, path_idx, seg_idx, pos):
    """Set Gate Position
    """
    # Determine start and end indexes of the position of current gate
    gate_pos_start_idx = (constants.G_GATE_IDX + (seg_idx
                          * constants.G_NUM_GATE_DIMS))
    gate_pos_end_idx = gate_pos_start_idx + constants.G_NUM_POS_DIMS

    # Set starting gate position
    path[path_idx, gate_pos_start_idx:gate_pos_end_idx] = pos

    return


def split_segments(data):
    """Split Segments

    Given full path data, split the path into segments of the path between
    gates. Samples of each segment are then outputted.

    Arguments:
        data: The path data from TrainingSim.

    Returns:
        A list of path segment data.
    """
    segment_list = []

    # Determine the start and end point for each segment
    segment_start = 0
    segment_ends = _detect_segments(data)

    for segment_end in segment_ends:
        # Split and store the data per segment
        segment_data = data[segment_start:segment_end]
        segment_list.append(segment_data)

        # Modify the next segment start
        segment_start = segment_end

    return segment_list


def get_ratings(data):
    """Get Ratings

    Given the full path data, return the ratings of each detected
    segment.

    Arguments:
        data: The path data from TrainingSim.

    Returns:
        Numpy array of each segment rating (Ratings in format: 0.0 - 1.0)
    """
    ratings = None

    # Find all segment ends
    segment_ends = _detect_segments(data)

    for segment_end in segment_ends:
        # Get the rating for each segment end
        segment_rating = data[segment_end][constants.G_RATING_IDX]

        # Convert from (0.0-1.0) to (1-4) scale
        segment_rating = (segment_rating * 4) + 1
        segment_rating = int(segment_rating)

        # Add it to the list
        if ratings is None:
            ratings = segment_rating
        else:
            ratings = np.vstack((ratings, segment_rating))

    # Return the ratings for the path
    return ratings

def rate_segments(data):
    """Rate Segments

    Given the full path data, the path segments between gates are
    determined and plotted. The user is then prompted to enter the
    the rating for each segment.

    Arguments:
        data: The path data from TrainingSim.

    Returns:
        The path data with user-defined segment ratings added.
    """
    ratings = None

    # Get the segment ends for easy rating
    segment_ends = _detect_segments(data)

    # The first segment will always start at 0th index
    segment_start = 0

    fig = plt.figure(facecolor='white')
    axis = fig.gca(projection='3d')

    fig.show()

    for idx, segment_end in enumerate(segment_ends):
        # Clear the axis so new data can be displayed
        axis.clear()

        # Display the current segment
        display_path(
            axis,
            data[segment_start:segment_end],
            dotted_paths=[data[:segment_start], data[segment_end:]],
            title=('Segment %d'%(idx+1))
        )

        # Draw the current segment on the figure
        plt.draw()

        while True:
            rating = raw_input('Enter segment %d rating (1 to 5): '%(idx+1))

            try:
                rating = int(rating)
            except ValueError:
                print('Invalid input. (1 to 5)')
                continue

            if rating < 1 or rating > 5:
                print('Invalid input. (1 to 5)')
                continue

            # Normalize rating between 0.0 and 1.0
            rating = float(rating)
            rating = (rating - 1.0) / 4.0

            # Create the rating for each epoch in the segment
            segment_rating = rating * np.ones((segment_end-segment_start, 1))

            if ratings is None:
                ratings = segment_rating
            else:
                ratings = np.vstack((ratings, segment_rating))

            break

        # Move next start index to current end index
        segment_start = segment_end

    # Smash the ratings on to the end column of the data matrix
    data = np.hstack((data, ratings))

    return data


if __name__ == '__main__':
    """Main

    If the module is directly called, the given file will be converted to
    a path dataset and plotted.

    Usage:
        ./pathutils.py [-h] [-t] [-n] [-f] [-i TITLE] [-o OUT] paths [paths ...] 
    """
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--trim',
                        help='trim the start and end of the path',
                        action='store_true')
    parser.add_argument('-n', '--normalize',
                        help='normalize path time',
                        action='store_true')
    parser.add_argument('-f', '--fix',
                        help='modify the initial position of the path',
                        action='store_true')
    parser.add_argument('-i', '--title',
                        help='specify output plot title',
                        action='store',
                        default=None)
    parser.add_argument('-o', '--out',
                        help='alternate path output',
                        action='store',
                        default=None)
    parser.add_argument('paths', nargs='+',
                        help='file(s) containing path data')
    parser.add_argument('-d', '--two-dimensional',
                        help='show 2d representation of the path (x, z)',
                        action='store_true')
    parser.add_argument('-a', '--label-axes',
                        help='show plot axes labels',
                        action='store_true')
    parser.add_argument('-r', '--ratings',
                        help='print out segment ratings along with the plot',
                        action='store_true')
    args = parser.parse_args()

    main_file = args.paths[0]
    main_path = datastore.retrieve(main_file)

    # Plot all reference paths
    reference_paths = []

    for reference_file in args.paths[1:]:
        reference_data = datastore.retrieve(reference_file)
        reference_paths.append(reference_data)

    # Trim if requested
    if args.trim:
        main_path = trim_path(main_path)

    # Normalize time if requested
    if args.normalize:
        main_path = normalize_time(main_path)

    # Fix starting position if requested
    if args.fix:
        main_path = fix_starting_pos(main_path)

    if args.ratings:
        ratings = get_ratings(main_path)

        for idx, rating in enumerate(ratings):
            print('Segment %d - Rating %d/5' % (idx, rating))

    # Plot the inputted path
    fig = plt.figure(facecolor='white')

    if not args.two_dimensional:
        axis = fig.gca(projection='3d')
    else:
        axis = fig.gca()

    axis.set_aspect('equal')

    display_path(axis, main_path, reference_paths, title=args.title, label_axes=args.label_axes, two_dimensional=args.two_dimensional)

    plt.show()

    if args.out is not None:
        datastore.store(main_path, args.out)
    else:
        datastore.store(main_path, args.paths[0])

    exit()
