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
import sys
import unittest

import pymnl
from pymnl.message import *

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

        self.seq = randint(1, pow(2, 31))
        self.msg._msg_seq = self.seq

        self.pid = randint(1, pow(2, 31))
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
        first_extra_header = Payload(pack("BBH", 3, 1, 0))
        self.msg.put_extra_header(first_extra_header)
        self.msg_length = self.msg_length + 4
        self.binary = (pack("I", self.msg_length) + self.msg_header +
                        first_extra_header.get_binary())
        self.assertEqual(self.msg.get_binary(), self.binary)
        # add a second copy of this header
        second_extra_header = Payload(pack("BBH", 3, 2, 0))
        self.msg.put_extra_header(second_extra_header)
        self.msg_length = self.msg_length + 4
        self.binary = (pack("I", self.msg_length) + self.msg_header +
                        first_extra_header.get_binary() +
                        second_extra_header.get_binary())
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

    def test_missing_payload(self):
        """ Test a message without a Payload.
        """
        self.assertRaises(UnboundLocalError, self.msg.get_binary)

    def test_ok(self):
        """ Test Message.ok().
        """
        self._setUp()
        self.assertTrue(self.msg.ok())

    def test_seq_ok(self):
        """ Test Message.seq_ok().

            Check that the sent sequence number and sequence number 0 are
            true and that a random integer does not match the sequence number.
        """
        self._setUp()
        # verify the sequence number tracked correctly
        self.assertTrue(self.msg.seq_ok(self.seq))
        # verify that sequence number zero is always true
        self.assertTrue(self.msg.seq_ok(0))
        # false positive is (remotely) possible if random number == seq
        self.assertFalse(self.msg.seq_ok(randint(1, pow(2, 31))))

    def test_printf_header(self):
        """ Test Message.printf_header().

            Check that printf_header synthetic output matches synthetic
            example.
        """
        self._setUp()
        expected_output = ['----------------\t------------------',
            '|  {0:0>10d}  |\t| message length |'.format(self.msg_length),
            '| {0:0>5d} | R-A- |\t|  type | flags  |'.format(self.msg._msg_type),
            '|  {0:0>10d}  |\t| sequence number|'.format(self.seq),
            '|  {0:0>10d}  |\t|     port ID    |'.format(self.pid),
            '----------------\t------------------']
        capture = PrintInterrupter()
        sys.stdout = capture
        self.msg.printf_header()
        sys.stdout = sys.__stdout__
        for exp_line, cap_line in zip(expected_output, capture.read_buffer()):
            self.assertEqual(exp_line, cap_line)

    def test_printf(self):
        """ Test Message.printf().

            Check that printf synthetic output matches previous capture.
        """
        # Not tested, yet
        pass

    def test_portid_ok(self):
        """ Test Message.portid_ok().

            Check that the sent portid number and portid number 0 are
            true and that a random integer does not match the portid number.
        """
        self._setUp()
        # verify the port id tracked correctly
        self.assertTrue(self.msg.portid_ok(self.pid))
        # verify that port id zero is always true
        self.assertTrue(self.msg.portid_ok(0))
        # false positive is (remotely) possible if random number == portid
        self.assertFalse(self.msg.portid_ok(randint(1, pow(2, 31))))

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
        # fake error to test all code branches, kinda pointless
        self.msg._msg_type = 0x2   # NLMSG_ERROR
        payload = Payload(pack("i", 2))
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


class TestPayload(unittest.TestCase):

    def test_init(self):
        """ Test init of a Payload.
        """
        # make a Payload from a binary data string
        payload1 = Payload(pack("BBH", 3, 1, 0))
        binary = pack("ssss", "\x03", "\x01", "\x00", "\x00")
        self.assertEqual(payload1.get_binary(), binary)
        # make a Payload from an existing Payload
        payload2 = Payload(payload1)
        self.assertEqual(payload2.get_binary(), binary)

    def test_printf(self):
        """ Test Payload.printf().

            Check that printf synthetic output matches synthetic
            example.
        """
        # make a Payload from a binary data string
        payload = Payload(pack("BBH", 3, 1, 0))
        expected_output = ['| 03 01 00 00  |\t|  extra header  |',
                           '----------------\t------------------']
        capture = PrintInterrupter()
        sys.stdout = capture
        payload.printf(16, 4)
        sys.stdout = sys.__stdout__
        for exp_line, cap_line in zip(expected_output, capture.read_buffer()):
            self.assertEqual(exp_line, cap_line)

    def test_add_attr(self):
        """ Test adding Attr objects to the Payload.
        """
        payload = Payload(pack("BBH", 3, 1, 0))
        binary = pack("ssss", "\x03", "\x01", "\x00", "\x00")
        self.assertEqual(payload.get_binary(), binary)

        family_type = Attr.new_u32(1, 16)
        payload.add_attr(family_type)
        binary = binary + pack("ssssssss",
                                            "\x08", "\x00", "\x01", "\x00",
                                            "\x10", "\x00", "\x00", "\x00")
        self.assertEqual(payload.get_binary(), binary)

        family_name = Attr.new_strz(2, b'nl80211')
        payload.add_attr(family_name)
        binary = binary + pack("ssssssssssss",
                                            "\x0c", "\x00", "\x02", "\x00",
                                            "n", "l", "8", "0",
                                            "2", "1", "1", "\x00")
        self.assertEqual(payload.get_binary(), binary)

    def test_empty_payload(self):
        """ Test an empty payload.
        """
        payload = Payload()
        self.assertEqual(payload.get_binary(), b'')

    @staticmethod
    def suite():
        return unittest.TestLoader().loadTestsFromTestCase(TestPayload)


class TestMessageList(unittest.TestCase):

    def setUp(self):
        """ Set up MessageList test.
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

    def test_init_from_message(self):
        """ Test MessageList creation from a Message instance.
        """
        msglist = MessageList(self.msg1)
        self.assertTrue(isinstance(msglist, MessageList))

    def test_init_from_binary_string(self):
        """ Test MessageList creation from a binary string.
        """
        self.assertTrue(isinstance(self.msglist, MessageList))

    def test_length(self):
        """ Test the number of Message's in the MessageList.
        """
        self.assertEqual(len(self.msglist), 3)

    def test_size(self):
        """ Test the total size (in bytes) of the MessageList.
        """
        # should be three messages long
        #   i.e. 3 * (header length + 24 byte payload)
        self.assertEqual(self.msglist.size(), (MSG_HDRLEN * 3) + (24 * 3))

    def test_failed_init(self):
        """
        """
        self.assertRaises(TypeError, MessageList, 2)

    @staticmethod
    def suite():
        return unittest.TestLoader().loadTestsFromTestCase(TestMessageList)


class PrintInterrupter(object):
    """ PrintInterrupter implements a write() method which accepts a string
        parameter.  Therefor, a PrintInterrupter object can be used in place
        of sys.stdout.

        The following doctest does not work because this class hacks stdout.

        >>> print("test 1")
        test 1
        >>> capture = PrintInterrupter()
        >>> sys.stdout = capture
        >>> print("test 2")
        >>> sys.stdout = sys.__stdout__
        >>> print("test 3")
        test 3
        >>> for buf_ in capture.read_buffer():
        ...    print(buf_)
        test 2
    """
    def __init__(self):
        """ Create a new, empty buffer to hold input. """
        self._buffer = []

    def write(self, str_):
        """ Accept a string and if it is not just a newline character,
            save it to our buffer.

            str_ - the string to add to the buffer
        """
        if (str_ != "\n"):
            self._buffer.append(str_)

    def read_buffer(self):
        """ Return the buffer contents as a list. """
        return self._buffer

