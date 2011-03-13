#!/usr/bin/python
# tests/genl.py -- tests generic netlink header and parsers
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

import pickle
import random
from struct import pack
import unittest

import pymnl
import pymnl.genl

class TestGenl(unittest.TestCase):

    def test_genlmsgheader(self):
        """ Test genetlink message header.
        """
        genlmh = pymnl.genl.GenlMessageHeader(
                                command=pymnl.genl.CTRL_CMD_GETFAMILY,
                                version=1)
        binary = pack("BBH", 3, 1, 0)
        self.assertEqual(genlmh.get_binary(), binary)

    def test_parsers(self):
        """ Test the various genetlink parsers.
        """
        # load pickled genetlink message
        f = open('pymnl/tests/genl-test_msg.pickled', 'rb')
        test_msg = pickle.load(f)
        f.close()
        # load pickled processed genetlink payload
        f = open('pymnl/tests/genl-test_attrs.pickled', 'rb')
        test_attrs = pickle.load(f)
        f.close()
        # process the test message
        genl_parser = pymnl.genl.GenlAttrParser()
        try:
            attrs = genl_parser.parse(test_msg.get_payload())
        except TypeError:
            # Unpickling a Py2 object with Py3 causes weirdness,
            payload = test_msg.get_payload()
            # so reach into the message payload and encode
            # the string as a bytes.
            payload._contents = payload._contents.encode()
            # Now we can parse the message payload for attributes.
            attrs = genl_parser.parse(payload)
            # convert expected bytes values to string
            attrs['name'] = attrs['name'].decode()
            attrs['groups'][1] = attrs['groups'][1].decode()
            attrs['groups'][2] = attrs['groups'][2].decode()
            attrs['groups'][3] = attrs['groups'][3].decode()
            attrs['groups'][4] = attrs['groups'][4].decode()
        # check that the pickled payload matches the processed payload
        self.assertEqual(test_attrs, attrs)

    @staticmethod
    def suite():
        return unittest.TestLoader().loadTestsFromTestCase(TestGenl)

