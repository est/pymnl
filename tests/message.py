#!/usr/bin/python
# tests/message.py -- test interface for netlink messages
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

from struct import pack
import unittest

import pymnl
from pymnl.message import *

class TestMessage(unittest.TestCase):

    @staticmethod
    def suite():
        return unittest.TestLoader().loadTestsFromTestCase(TestMessages)


class TestPayload(unittest.TestCase):

    def _test_init(self):
        """ Test init of a Payload.
        """
        self.payload = Payload(pack("BBH", 3, 1, 0))
        self.binary = pack("ssss", "\x03", "\x01", "\x00", "\x00")
        self.assertEqual(self.payload.get_binary(), self.binary)

    def _test_add_attr(self):
        """ Test adding Attr objects to the Payload.
        """
        self.family_type = Attr.new_u32(1, 16)
        self.payload.add_attr(self.family_type)
        self.binary = self.binary + pack("ssssssss",
                                            "\x08", "\x00", "\x01", "\x00",
                                            "\x10", "\x00", "\x00", "\x00")
        self.assertEqual(self.payload.get_binary(), self.binary)

        self.family_name = Attr.new_strz(2, b'nl80211')
        self.payload.add_attr(self.family_name)
        self.binary = self.binary + pack("ssssssssssss",
                                            "\x0c", "\x00", "\x02", "\x00",
                                            "n", "l", "8", "0",
                                            "2", "1", "1", "\x00")
        self.assertEqual(self.payload.get_binary(), self.binary)

    def test_payload(self):
        """ Call private test methods which build a Payload step-by-step.
        """
        self._test_init()
        self._test_add_attr()

    def tearDown(self):
        """ Clean up after each test.
        """
        self.payload = None

    @staticmethod
    def suite():
        return unittest.TestLoader().loadTestsFromTestCase(TestPayload)


