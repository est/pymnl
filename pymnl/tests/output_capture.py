#!/usr/bin/python
# output_capture -- catch stdout in a deque
# Copyright (c) 2011 Sean Robinson <seankrobinson@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from collections import deque
import sys

class OutputCapture(object):
    """ A context manager to capture stdout in memory, then provide a
        generator (readlines) to read the captured lines of output.  Internal
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

