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
"""


# Import external modules
import cPickle

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
        cPickle.dump(data, f)

    return


def retrieve(filename):
    """Retrieve Data

    Returns all pickled data in the specified filename as a Python object.

    Arguments:
        filename: The filename containing the pickled object data.

    Returns:
        The unpickled Python object.
    """
    with open(filename, 'r') as f:
        data = cPickle.load(f)

    return data


def split_data(raw_data):
    inputs = []
    outputs = []

    for sample in raw_data:
        inputs.append(sample[0])
        outputs.append(sample[1])

    return inputs, outputs


def files_to_dataset(filenames):
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

    Returns:
        A SequentialDataSet object built from the retrieved input/output data.
    """
    dataset = None

    for filename in filenames:
        # Get all Python object data from the pickled file
        raw_data = retrieve(filename)

        # Unpack the Python object data into inputs/outputs
        inputs, outputs = split_data(raw_data)

        # The dataset object has not been initialized. We must determine the
        # input and output size based on the unpacked data
        if dataset is None:
            dataset = SequentialDataSet(
                0,#len(inputs[0]),
                len(outputs[0])
            )

        # Create a new sequence of data for this file
        dataset.newSequence()

        # Create a new sample for each input/output pair in the sequence
        for i, input in enumerate(inputs):
            output = outputs[i]
            #dataset.addSample(input, output)
            dataset.addSample([], output)

    return dataset


if __name__ == '__main__':
    pass
