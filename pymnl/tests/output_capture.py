#!/usr/bin/python

from collections import deque
import sys

class OutputCapture(object):
    """ A context manager to capture stdout in memory, then provide a
        generator (readline) to read the captured lines of output.  Internal
        storage of the captured line is handled by a collections.deque
        object.

        >>> print("test 1")
        test 1
        >>> with OutputCapture(3) as capture:
        ...     print("|------- test -------|")
        ...     print("|----- {0} -----|".format("fmt test"))
        ...     print("|--------------------|")
        ...     print("|----- end test -----|")
        ...
        >>> print("test 2")
        test 2
        >>> for line in capture.readlines():
        ...     print(line)
        ...
        |----- fmt test -----|
        |--------------------|
        |----- end test -----|

    """
    def __init__(self, max_size=None):
        """ Create an OutputCapture object.

            max_size is the maximum number of lines to capture.  The default
                is limitted only by memory.  Adding data beyond max_size
                lines will cause the oldest lines to be discarded so that
                the new lines can be stored.
        """
        self.buffer_ = deque(maxlen=max_size)

    def __enter__(self):
        self.old_stdout = sys.stdout
        sys.stdout = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self.old_stdout
        return False

    def write(self, data):
        """ Receive data from a file writer (e.g. print).  Do not call this
            directly.  This method does not save newline-only lines.
        """
        if (data != "\n"):
            self.buffer_.append(data)

    def readlines(self):
        """ Return a generator for the captured lines.
        """
        for line in self.buffer_:
            yield line

