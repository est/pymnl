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

from random import randint
from struct import pack
import unittest

import pymnl
from pymnl.message import *

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


class TestMessage(unittest.TestCase):

    def setUp(self):
        """ Set up the initial conditions for each test.
        """
        self.msg = Message()

    def _setUp(self):
        """ Set up the initial conditions for some tests.

            Creates hypothetical genl protocol for more complicated tests.
        """
        self.msg._msg_type = 16  # GENL_ID_CTRL
        self.msg._msg_flags = 5  # NLM_F_REQUEST | NLM_F_ACK

        self.seq = randint(0, pow(2, 31))
        self.msg._msg_seq = self.seq

        self.pid = randint(0, pow(2, 31))
        self.msg._pid = self.pid

        self.msg_length = 16
        self.msg_header = pack("HHII", self.msg._msg_type,
                                       self.msg._msg_flags,
                                       self.seq, self.pid)

    def _test_valid_header_values(self, set_method_, get_method_,
                                min_value_, max_value_):
        """ Test a Message header accessor with valid values.
        """
        random_ = randint(min_value_ + 1, max_value_ - 1)
        for value_ in (min_value_, random_, max_value_):
            set_method_(self.msg, value_)
            self.assertEqual(get_method_(self.msg), value_,
                            "returned value does not match entered value")

    def _test_invalid_header_values(self, set_method_, get_method_,
                                        min_value_, max_value_):
        """ Test a Message header accessor with invalid values.
        """
        random_ = randint(min_value_ + 1, max_value_ - 1)
        for value_ in (min_value_, random_, max_value_):
            self.assertRaises(ValueError, set_method_, self.msg, value_)

    def test_type(self):
        """ Test valid and invalid type values.
        """
        self._test_valid_header_values(Message.set_type, Message.get_type,
                                        0, 0xffff)
        self._test_invalid_header_values(Message.set_type, Message.get_type,
                                            0xffff + 1, 0xffffffff)

    def test_flags(self):
        """ Test valid and invalid flags values.
        """
        self._test_valid_header_values(Message.set_flags, Message.get_flags,
                                        0, 0xffff)
        self._test_invalid_header_values(Message.set_flags, Message.get_flags,
                                            0xffff + 1, 0xffffffff)

    def test_seq(self):
        """ Test valid and invalid sequence numbers.
        """
        self._test_valid_header_values(Message.set_seq, Message.get_seq,
                                        0, 0xffffffff)
        self._test_invalid_header_values(Message.set_seq, Message.get_seq,
                                        0xffffffff + 1, 0xffffffffffffffff)

    def test_portid(self):
        """ Test valid and invalid portid values.
        """
        self._test_valid_header_values(Message.set_portid,
                                        Message.get_portid,
                                        0, 0xffffffff)
        self._test_invalid_header_values(Message.set_portid,
                                         Message.get_portid,
                                         0xffffffff + 1, 0xffffffffffffffff)

    def test_put_extra_header(self):
        """ Test Message.put_extra_header().
        """
        self._setUp()
        # add a four byte header object
        extra_header = Payload(pack("BBH", 3, 1, 0))
        self.msg.put_extra_header(extra_header)
        self.msg_length = self.msg_length + 4
        self.binary = (pack("I", self.msg_length) + self.msg_header +
                        extra_header.get_binary())
        self.assertEqual(self.msg.get_binary(), self.binary)

    def test_add_payload(self):
        """ Test Message.add_payload().
        """
        self._setUp()
        payload = Payload(pack("BBH", 3, 1, 0))
        self.msg.add_payload(payload)
        self.msg_length = self.msg_length + 4
        self.binary = (pack("I", self.msg_length) + self.msg_header +
                        payload.get_binary())
        self.assertEqual(self.msg.get_binary(), self.binary)

    def test_get_payload(self):
        """ Test Message.get_payload().

            In reality, this justs tests that all the names for the same
            object point to the same object.  I.E. this is not much of
            a test.
        """
        self._setUp()
        payload_in = Payload(pack("BBH", 3, 1, 0))
        self.msg.add_payload(payload_in)
        payload_out = self.msg.get_payload()
        self.assertEqual(payload_in, payload_out)

    def test_ok(self):
        """ Test Message.ok().
        """
        self._setUp()
        self.assertTrue(self.msg.ok())

    def test_seq_ok(self):
        """ Test Message.seq_ok().

            Check that initial sequence number is still used and that
            a random integer does not match the sequence number.
        """
        self._setUp()
        self.assertTrue(self.msg.seq_ok(self.seq))
        # false result possible if random number == seq
        self.assertFalse(self.msg.seq_ok(randint(0, pow(2, 31))))

    def test_portid_ok(self):
        """ Test Message.portid_ok().

            Check that initial portid number is still used and that
            a random integer does not match the portid number.  In
            real-world use, generally, portid is sent as 0 and is
            assigned another number by the kernel.
        """
        self._setUp()
        self.assertTrue(self.msg.portid_ok(self.pid))
        # false result possible if random number == portid
        self.assertFalse(self.msg.portid_ok(randint(0, pow(2, 31))))

    def test_get_errno(self):
        """ Test Message.get_errno().
        """
        self._setUp()
        # no error code
        payload = Payload(pack("i", 0))
        self.msg.add_payload(payload)
        self.msg_length = self.msg_length + 4
        self.assertEqual(self.msg.get_errno(), 0)
        # ENOENT error
        self.msg._msg_type = 0x2   # NLMSG_ERROR
        payload = Payload(pack("i", -2))
        self.msg._payload = payload
        self.assertEqual(self.msg.get_errno(), 2)

    def test_get_errstr(self):
        """ Test Message.get_errstr().
        """
        self._setUp()
        # no error code
        payload = Payload(pack("i", 0))
        self.msg.add_payload(payload)
        self.msg_length = self.msg_length + 4
        self.assertEqual(self.msg.get_errstr(), 'Success')
        # ENOENT error
        self.msg._msg_type = 0x2   # NLMSG_ERROR
        payload = Payload(pack("i", -2))
        self.msg._payload = payload
        self.assertEqual(self.msg.get_errstr(), 'No such file or directory')

    def tearDown(self):
        """ Clean up after each test.
        """
        self.msg = None

    @staticmethod
    def suite():
        return unittest.TestLoader().loadTestsFromTestCase(TestMessage)


class TestMessageList(unittest.TestCase):

    def test_msglist(self):
        """
        """
        self.payload = Payload(b'\x03\x01\x00\x00\x08\x00\x01\x00\x10\x00\x00\x00\x0c\x00\x02\x00nl80211\x00')
        self.msg1 = Message()
        self.msg1.add_payload(self.payload)
        self.msg2 = Message()
        self.msg2.add_payload(self.payload)
        self.msg3 = Message()
        self.msg3.add_payload(self.payload)
        self.msg = (self.msg1.get_binary() + self.msg2.get_binary() +
                        self.msg3.get_binary())
        self.msglist = MessageList(self.msg)
        self.assertEqual(len(self.msglist), 3)

    @staticmethod
    def suite():
        return unittest.TestLoader().loadTestsFromTestCase(TestMessageList)

