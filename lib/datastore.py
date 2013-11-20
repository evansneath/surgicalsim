#!usr/bin/env python

"""DataStore module

Stores and retrieves saved ("pickled") data to/from a given file.

Author:
    Evan Sneath - evansneath@gmail.com

License:
    Open Software License v3.0

Functions:
    store: Stores data in the specified file.
    retrieve: Returns data from the specified file.
    files_to_dataset: Given a list of files containing pickled input and output
        data from the TrainingSim application, a new SequentialDataSet class
        object is returned.
    list_to_dataset: Converts a input/output sequence pair into a
        SequentialDataSet class object.
"""


# Import external modules
import numpy as np

# Import pybrain sequential data module
from pybrain.datasets.sequential import SequentialDataSet


def store(data, filename):
    """Store Data

    Writes all given data into the specified filename in a pickled format.

    Arguments:
        data: The Python object to pickle.
        filename: The filename into which the pickled data should be written.
            If the given file does not exist, it is created.
    """
    with open(filename, 'w+') as f:
        np.save(f, data)

    return


def retrieve(filename):
    """Retrieve Data

    Returns all pickled data in the specified filename as a Python object.

    Arguments:
        filename: The filename containing the pickled object data.

    Returns:
        The unpickled Python object.
    """
    data = np.load(filename)
    return data


def split_data(time_data, num_inputs):
    """Split Data

    Splits time sequence data of input, output into separated, transposed
    arrays.

    Arguments:
        time_data: The raw time sequence array of input, output data.
        num_inputs: The number of input fields present in each time step of
            the array.

    Returns:
        (input_data, output_data) - Two arrays of the input and output data
        organized in [dim x time] format (transposed from original).
    """
    # Split the array depending on the numbers of inputs
    return time_data[:, :num_inputs], time_data[:, num_inputs:]


def files_to_dataset(filenames, num_inputs, dataset=None):
    """Files to Dataset

    Given a list of filenames containing raw training data, the filenames
    will be inspected and a new sequential dataset will be created with each
    file's data for use in neural network training.

    Arguments:
        filenames: A list of filenames containing pickled captured data. The
            pickled data must be stored in the following format:
            [([input1, input2, ...], [output1, output2, ...]), ...]
            where each tuple represents a single sample containing a set of
            flat input and flat output arrays.
        num_inputs: The number of inputs prepending the outputs for each time
            step.
        dataset: A SequentialDataSet object to add a new sequence. New dataset
            generated if None. (Default: None)

    Returns:
        A SequentialDataSet object built from the retrieved input/output data.
    """
    for filename in filenames:
        # Get all Python object data from the pickled file
        data = retrieve(filename)

        # Unpack the Python object data into inputs/outputs
        inputs, outputs = split_data(data, num_inputs)

        dataset = list_to_dataset(inputs, outputs, dataset)

    return dataset


def list_to_dataset(inputs, outputs, dataset=None):
    """List to Dataset

    Convert a standard list to a dataset. The list must be given in the
    following format:

        Inputs: 2 dimension list (N x M)
        Outputs: 2 dimension list (N x K)

        N: Number of time steps in data series
        M: Number of inputs per time step
        K: Number of outputs per time step

    Arguments:
        inputs: The input list given under the above conditions.
        outputs: The output list given under the above conditions.
        dataset: A SequentialDataSet object to add a new sequence. New dataset
            generated if None. (Default: None)

    Returns:
        A SequentialDataSet object built from the retrieved input/output data.
    """
    assert len(inputs) > 0
    assert len(outputs) > 0
    assert len(inputs) == len(outputs)

    # The dataset object has not been initialized. We must determine the
    # input and output size based on the unpacked data
    num_samples = len(inputs)
    in_dim = len(inputs[0])
    out_dim = len(outputs[0])

    # If the dataset does not exist, create it. Otherwise, use the dataset
    # given
    if not dataset:
        dataset = SequentialDataSet(in_dim, out_dim)

    # Make a new sequence for the given input/output pair
    dataset.newSequence()

    for i in range(num_samples):
        dataset.addSample(inputs[i], outputs[i])

    return dataset


if __name__ == '__main__':
    pass
