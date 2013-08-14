#!/usr/bin/env python2.7

import time
import multiprocessing

G_SLEEPTIME = 1

class TestThread(multiprocessing.Process):
    """TestThread class

    A simple subclass of multiprocessing.Process class which takes a shared
    value object and uses a lock object to securely increment the shared
    value object forever in the run() method loop.
    """
    def __init__(self, data):
        super(TestThread, self).__init__()

        # Store the shared value object and the lock object
        self._data = data
        self._lock = multiprocessing.Lock()

        return


    def run(self):
        """Run

        This subclasses the multiprocessing.Process.run() method. The run
        method is called during Process.start(). This particular implementation
        loops and modifies the shared value object forever.
        """
        global G_SLEEPTIME

        while True:
            time.sleep(G_SLEEPTIME)

            # Lock the shared value to prevent read/write conflicts
            with self._lock:
                self._data.value += 1
    
        return


def main():
    global G_SLEEPTIME

    # Create a shared value
    data = multiprocessing.Value('i', 0)

    # Populate a new test thread
    t = TestThread(data)

    # Start the test thread object. This creates a new process
    t.start()

    # Continue to print the newest data populated by the thread into the
    # shared value object
    while True:
        print data.value

        # By sleeping in the main thread x4 as long as in the in the spawned
        # TestThread object, we can verify that every print shows the shared
        # object incremented by 4. This proves that we are always getting the
        # newest data from the spawned thread.
        time.sleep(G_SLEEPTIME * 4)

    return

if __name__ == '__main__':
    main()
