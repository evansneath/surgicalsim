#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

import surgicalsim.lib.constants as constants
import surgicalsim.lib.pathutils as pathutils
import surgicalsim.lib.datastore as datastore

def main():
    """
    PLOT GENERATED PATH VS TRAINING PATH
    """
    # Define generated and trained data file names
    generated_file = '../../results/generated/rnn-path.dat'

    trained_files = [
            '../../results/sample1.dat',
            '../../results/sample2.dat',
            '../../results/sample3.dat',
            '../../results/sample4.dat',
            '../../results/sample5.dat',
    ] 

    # Collect data from the files
    generated_path = datastore.retrieve(generated_file)

    trained_paths = []
    for file in trained_files:
        path_data = datastore.retrieve(file)
        trained_paths.append(path_data)

    # Calculate the closest point for each path to the markers
    generated_distances = calculate_closest_approaches(generated_path)

    trained_distances = []
    for path in trained_paths:
        distances = calculate_closest_approaches(path)
        trained_distances.append(distances)

    # Number of indicies in the chart (each marker)
    indices = np.arange(constants.G_NUM_GATES)

    # Width of the bars in the bar chart
    width = 0.1

    plt.subplots(facecolor='white')

    # Draw the generated path's closest approaches
    plt.bar(indices, generated_distances, width, color='b', label='generated path')

    # Draw the closest approaches for all trained paths
    for idx, distances in enumerate(trained_distances):
        this_label = None

        if idx == 0:
            this_label = 'training path'

        plt.bar(indices+(width*(idx+1)), distances, width, color='r', label=this_label)

    plt.xlabel('Marker Number')
    plt.xlim(right=indices[-1]+(width+(width*len(trained_files))))
    plt.ylabel('Distance of Closest Approach [m]')
    plt.title('Distance of Closest Approach of Tooltip to Each Marker (Generated vs Training Paths)')
    plt.legend()

    plt.show()

    """
    PLOT DYNAMIC VS STATIC PATH CLOSEST APPROACH
    """
    # Define files holding the static and dynamic path data
    dynamic_file = '../../results/generated/final-path.dat'
    static_file = '../../results/generated/rnn-path.dat'

    # Retrieve the path data from these files
    dynamic_path = datastore.retrieve(dynamic_file)
    static_path = datastore.retrieve(static_file)

    # Calculate distances of closest approach
    dynamic_distances = calculate_closest_approaches(dynamic_path)
    static_distances = calculate_closest_approaches(static_path)

    width = 0.2

    # Clear the current plot
    plt.cla()

    # Plot the distance of closest approach of the paths to each marker
    plt.subplots(facecolor='white')

    plt.bar(indices, dynamic_distances, width, color='b', label='dynamic path')
    plt.bar(indices+width, static_distances, width, color='r', label='static path')

    plt.xlabel('Marker Number')
    plt.xlim(right=indices[-1]+(width*2))
    plt.ylabel('Distance of Closest Approach [m]')
    plt.title('Distance of Closest Approach of Tooltip to Each Marker (Dynamic vs Static Paths)')
    plt.legend()

    plt.show()
   
    return


def calculate_closest_approaches(path):
    """Calculate Closest Approaches

    Given a standard SurgicalSim path, the closest approaches of that path to
    each marker will be calculated.

    Arguments:
        path: A SurgicalSim formatted path.

    Returns:
        A list of distances of size N, where N is the number of markers.
    """
    segments = pathutils._detect_segments(path)

    distances = []

    for gate_idx in np.arange(constants.G_NUM_GATES):
        x_gate = pathutils.get_path_gate_pos(path, segments[gate_idx], gate_idx)
        x_tooltip = pathutils.get_path_tooltip_pos(path, segments[gate_idx])

        dist = np.sqrt((x_gate[0] - x_tooltip[0]) ** 2 + (x_gate[1] - x_tooltip[1]) ** 2 + (x_gate[2] - x_tooltip[2]) ** 2)
        distances.append(dist)

    return distances


if __name__ == '__main__':
    main()
    exit()
