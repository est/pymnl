#!/usr/bin/python
# test -- implements a test command for distutils.core.setup
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

import distutils.core
import imp
import re
import unittest

class test(distutils.core.Command):
    """ Run unit tests.

        This command loads the modules specified with --test-list=
        (e.g. --test-list=tests.message,tests.attributes) and looks in
        each for class names starting with 'Test'.  This is similar to the
        way unittest.TestLoader looks for test cases as method names
        beginning with 'test'.

        This command then queries each found class for its test suite
        using an expected suite() static method which returns the test
        cases found by unittest.TestLoader().loadTestsFromTestCase(TestClass).

        Then the tests are run using unittest.TextTestRunner() with a
        default verbosity of 0, or a verbosity of 2 if the --test-verbose
        option is passed to the command.

        This class seems to work with Python > 2.6.
    """
    description = "Run unit tests."

    # List of option tuples: long name, short name (None if no short
    # name), and help string.
    user_options = [('test-list=', None,
                     "list of test modules to run " +
                     "(e.g. tests.message)"),
                    ('test-verbose', None,
                     "show additional output during tests"),
                   ]

    boolean_options = ['test-verbose']

    def initialize_options(self):
        """ Set the default values for command options.
        """
        self.test_list = None
        self.test_verbose = 0

    def finalize_options(self):
        """ Ensure options are ready to be used during test set-up.
        """
        if self.test_list:
            self.test_list = re.split(",", self.test_list)
        else:
            self.test_list = []
        if (self.test_verbose):
            self.test_verbose = 2

    def load_module(self, mod_name, path=None):
        """ Recursively work down a module hierarchy to load the
            module at the bottom of the list.

            mod_name - string with the name of the module to load,
                        e.g. "tests.message" (see imp.find_module())

            path - list of directories to search (see imp.find_module())

            Returns an instance of the loaded module.
        """
        hierarchy = re.split("\.", mod_name)
        mod_specs = imp.find_module(hierarchy[0], path)
        try:
            module = imp.load_module(hierarchy[0], mod_specs[0],
                                                mod_specs[1], mod_specs[2])
        finally:
            if (mod_specs[0]):
                mod_specs[0].close()
        if (len(hierarchy) > 1):
            module = self.load_module(".".join(hierarchy[1:]),
                                                        module.__path__)
        return module

    def run(self):
        """ Find and load module(s) with test classes, ask those classes
            for a test suite, and run the returned tests.
        """
        test_class_pattern = re.compile("Test")
        for test_module in self.test_list:
            test_module = self.load_module(test_module)
            for module_attr in dir(test_module):
                result = test_class_pattern.match(module_attr)
                if (result):
                    class_ = test_module.__getattribute__(module_attr)
                    suite = class_.suite()
                    unittest.TextTestRunner(verbosity=self.test_verbose).run(suite)

