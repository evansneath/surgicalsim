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
"""


import cPickle


def store(self, data, filename):
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


def retrieve(self, filename):
    """Retrieve Data

    Returns all pickled data in the specified filename as a Python object.

    Arguments:
        filename: The filename containing the pickled object data.

    Returns:
        The unpickled Python object.
    """
    with open(filename, 'w') as f:
        data = cPickle.load(f)

    return data
