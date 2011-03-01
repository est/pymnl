#!/usr/bin/python
# tests/unittests.py -- test interface for pymnl
# Copyright 2011 Sean Robinson <seankrobinson@gmail.com>
#
# This file is part of the pymnl package, a Python interface
# for netlink sockets.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public License
#  as published by the Free Software Foundation; either version 2.1 of
#  the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
#  USA
#

from __future__ import print_function

import unittest

import tests.nlsocket
import tests.attributes
import tests.message

# list of 2-tuples with name and test case
test_cases = [ ("Socket", tests.nlsocket.TestSocket),
               ("Attr", tests.attributes.TestAttributes),
               ("Payload", tests.message.TestPayload),
               ("Message", tests.message.TestMessage),
               ("MessageList", tests.message.TestMessageList) ]

for (name, test_case) in (test_cases):
    suite = test_case.suite()
    results = unittest.TestResult()
    suite.run(results)
    print(name, "tests run:", results.testsRun)
    print(name, "errors:", len(results.errors))
    for error in results.errors:
        print(error[0], "-", error[1])
    print(name, "failed tests:", len(results.failures))
    for failure in results.failures:
        print(failure[0], "-", failure[1])

