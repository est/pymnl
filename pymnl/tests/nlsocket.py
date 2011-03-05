#!/usr/bin/python
# tests/nlsocket.py -- test interface to netlink socket
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

import random
import unittest

import pymnl
from pymnl.nlsocket import Socket

class TestSocket(unittest.TestCase):

    def setUp(self):
        """ Set up conditions necessary for each test.
        """
        self.nl_socket = Socket(pymnl.NETLINK_GENERIC)
        self._pid = random.randint(1024, 32768)
        self._groups = 0
        self.nl_socket.bind(self._pid, self._groups)

    def test_bus(self):
        """ Test that the requested bus is the actual bus.
        """
        self.assertEqual(self.nl_socket._bus, pymnl.NETLINK_GENERIC)

    def test_pid(self):
        """ Test that the requested port id is the actual port id.
        """
        self.assertEqual(self.nl_socket.get_portid(), self._pid)

    def test_groups(self):
        """ Test that the requested groups is the actual groups.
        """
        self.assertEqual(self.nl_socket.get_groups(), self._groups)

    def tearDown(self):
        """ Clean up after each test.
        """
        self.nl_socket.close()

    @staticmethod
    def suite():
        return unittest.TestLoader().loadTestsFromTestCase(TestSocket)


