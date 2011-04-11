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
from pymnl.tests.output_capture import OutputCapture

class TestMessage(unittest.TestCase):

    def setUp(self):
        """ Set up the initial conditions for each test.
        """
        # message type is GENL_ID_CTRL (or 16)
        # message flags is NLM_F_REQUEST | NLM_F_ACK (or 5)
        self.msg, self.bin_str = self._build_message(16, 5)

    def _build_message(self, type_, flags_, seq_=None, pid_=None,
                                                            header_=None):
        """ Return a list with a Message object and a binary string
            representation which can be used for testing.

            type_ - integer - Netlink message type

            flags_ - integer - Netlink message flags

            seq_ - integer - Netlink message's sequence number

            pid_ - integer - Netlink message's port id

            header_ - binary string - an extra header to add to the Message
        """
        msg = Message()
        msg._msg_type = type_
        msg._msg_flags = flags_
        if (not seq_):
            seq_ = randint(1, pow(2, 31))
        msg._msg_seq = seq_
        if (not pid_):
            pid_ = randint(1, pow(2, 31))
        msg._pid = pid_
        length = 16
        msg._msg_length = length

        binary = pack("ihhii", length, type_, flags_, seq_, pid_)
        return (msg, binary)

    def _add_length(self, binary, length):
        """ Replace the encoded length in a binary string representing a
            Message object.

            binary - binary string - the representation to update

            length - integer - the delta from the current length (4 means
                add 4 bytes, -8 means subtract 8 bytes)
        """
        payload = binary[16:]
        header = binary[:16]
        header_list = list(unpack("ihhii", header))
        header_list[0] += length
        return pack("ihhii", *header_list) + payload

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
        # add a four byte header object
        first_extra_header = Payload(pack("BBH", 3, 1, 0))
        self.msg.put_extra_header(first_extra_header)
        self.bin_str = self.bin_str + first_extra_header.get_binary()
        self.bin_str = self._add_length(self.bin_str, 4)
        self.assertEqual(self.msg.get_binary(), self.bin_str)

        # add a second copy of this header
        second_extra_header = Payload(pack("BBH", 3, 2, 0))
        self.msg.put_extra_header(second_extra_header)
        self.bin_str = self.bin_str + second_extra_header.get_binary()
        self.bin_str = self._add_length(self.bin_str, 4)
        self.assertEqual(self.msg.get_binary(), self.bin_str)

    def test_add_payload(self):
        """ Test Message.add_payload().
        """
        payload = Payload(pack("BBH", 3, 1, 0))
        self.msg.add_payload(payload)
        self.bin_str = self.bin_str + payload.get_binary()
        self.bin_str = self._add_length(self.bin_str, 4)
        self.assertEqual(self.msg.get_binary(), self.bin_str)

    def test_get_payload(self):
        """ Test Message.get_payload().

            In reality, this justs tests that all the names for the same
            object point to the same object.  I.E. this is not much of
            a test.
        """
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
        self.assertTrue(self.msg.ok())

    def test_seq_ok(self):
        """ Test Message.seq_ok().

            Check that the sent sequence number and sequence number 0 are
            true and that a random integer does not match the sequence number.
        """
        seq = randint(1, pow(2, 31))
        message, bs = self._build_message(16, 5, seq_=seq)
        # verify the sequence number tracked correctly
        self.assertTrue(message.seq_ok(seq))
        # verify that sequence number zero is always true
        self.assertTrue(message.seq_ok(0))
        # false positive is (remotely) possible if random number == seq
        self.assertFalse(message.seq_ok(randint(1, pow(2, 31))))

    def _translate_flags(self, flags):
        """ Translate message flags integer to 4 char string.

            NLM_F_REQUEST = 1 = R
            NLM_F_MULTI = 2 = M
            NLM_F_ACK = 4 = A
            NLM_F_ECHO = 8 = E
        """
        flags_list = ["-"] * 4
        if (flags & 1):
            flags_list[0] = "R"
        if (flags & 2):
            flags_list[1] = "M"
        if (flags & 4):
            flags_list[2] = "A"
        if (flags & 8):
            flags_list[3] = "E"
        return ''.join(flags_list)

    def test_printf_header(self):
        """ Test Message.printf_header().

            Check that printf_header synthetic output matches synthetic
            example.
        """
        for flags in [pow(2, x) for x in range(4)]:
            type_ = 16
            seq = randint(1, pow(2, 31))
            pid = randint(1, pow(2, 31))
            message, bs = self._build_message(type_, flags, seq_=seq, pid_=pid)
            expected_output = ['----------------\t------------------',
                '|  {0:0>10d}  |\t| message length |'.format(len(bs)),
                '| {0:0>5d} | {1} |\t|  type | flags  |'.format(type_, self._translate_flags(flags)),
                '|  {0:0>10d}  |\t| sequence number|'.format(seq),
                '|  {0:0>10d}  |\t|     port ID    |'.format(pid),
                '----------------\t------------------']
            with OutputCapture(25) as capture:
                message.printf_header()
            for exp_line, cap_line in zip(expected_output, capture.readlines()):
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
        pid = randint(1, pow(2, 31))
        message, bs = self._build_message(16, 5, pid_=pid)
        # verify the port id tracked correctly
        self.assertTrue(message.portid_ok(pid))
        # verify that port id zero is always true
        self.assertTrue(message.portid_ok(0))
        # false positive is (remotely) possible if random number == portid
        self.assertFalse(message.portid_ok(randint(1, pow(2, 31))))

    def test_get_errno(self):
        """ Test Message.get_errno().
        """
        # no error code
        payload = Payload(pack("i", 0))
        self.msg.add_payload(payload)
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
        # no error code
        payload = Payload(pack("i", 0))
        self.msg.add_payload(payload)
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
        self.bin_str = None

    @staticmethod
    def load_tests(loader, tests, pattern):
        """ Return tests from class.  Fake implementation of the load_tests
            protocol from Michael Foord's discover.py.

            loader, tests, and pattern do not do anything, yet
        """
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

    def test_printf_control_message(self):
        """ Test Payload.printf() with a control message.

            Check that printf synthetic output matches synthetic
            example.
        """
        # make a Payload from a binary data string
        payload = Payload(pack("BBH", 3, 1, 0))
        expected_output = ['| 03 01 00 00  |\t|                |',
                           '----------------\t------------------']
        with OutputCapture(25) as capture:
            # error message (control message 2 is an error returned for decoding)
            payload.printf(2, 0)
        for exp_line, cap_line in zip(expected_output, capture.readlines()):
            self.assertEqual(exp_line, cap_line)

    def test_printf_extra_header(self):
        """ Test Payload.printf() with an extra header.

            Check that printf synthetic output matches synthetic
            example.
        """
        # make a Payload from a binary data string
        payload = Payload(pack("BBH", 3, 1, 0))
        expected_output = ['| 03 01 00 00  |\t|  extra header  |',
                           '----------------\t------------------']
        with OutputCapture(25) as capture:
            payload.printf(16, 4)
        for exp_line, cap_line in zip(expected_output, capture.readlines()):
            self.assertEqual(exp_line, cap_line)

    def test_printf_with_attr(self):
        """ Test Payload.printf() with an attribute.

            Check that printf synthetic output matches synthetic
            example.
        """
        # make a Payload from a binary data string
        payload = Payload()
        payload.add_attr(pymnl.attributes.Attr.new_u32(3, 42))
        expected_output = ['|\x1b[1;31m00008\x1b[0m|\x1b[1;32m--\x1b[0m|\x1b[1;34m00003\x1b[0m|\t|len |flags| type|',
                           '| 2a 00 00 00  |\t|      data      |\t \x00 \x00 \x00 \x00',
                           '----------------\t------------------']
        with OutputCapture(25) as capture:
            payload.printf(16, 0)
        for exp_line, cap_line in zip(expected_output, capture.readlines()):
            self.assertEqual(exp_line, cap_line)

    def test_printf_with_nested_attr(self):
        """ Test Payload.printf() with a nested attribute.

            Check that printf synthetic output matches synthetic
            example.
        """
        one_attr = pymnl.attributes.Attr.new_u32(3, 42)
        one_attr.toggle_nested()
        payload = Payload()
        payload.add_attr(one_attr)
        expected_output = ['|\x1b[1;31m00008\x1b[0m|\x1b[1;32mN-\x1b[0m|\x1b[1;34m00003\x1b[0m|\t|len |flags| type|',
                           '----------------\t------------------']
        with OutputCapture(25) as capture:
            payload.printf(16, 0)
        for exp_line, cap_line in zip(expected_output, capture.readlines()):
            self.assertEqual(exp_line, cap_line)

    def test_printf_with_network_byteorder_attr(self):
        """ Test Payload.printf() with a network byte-order attribute.

            Check that printf synthetic output matches synthetic
            example.
        """
        one_attr = pymnl.attributes.Attr.new_u32(3, 42)
        one_attr._type = one_attr._type ^ pymnl.attributes.NLA_F_NET_BYTEORDER
        payload = Payload()
        payload.add_attr(one_attr)
        expected_output = ['|\x1b[1;31m00008\x1b[0m|\x1b[1;32m-B\x1b[0m|\x1b[1;34m00003\x1b[0m|\t|len |flags| type|',
                           '| 2a 00 00 00  |\t|      data      |\t \x00 \x00 \x00 \x00',
                           '----------------\t------------------']
        with OutputCapture(25) as capture:
            payload.printf(16, 0)
        for exp_line, cap_line in zip(expected_output, capture.readlines()):
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
    def load_tests(loader, tests, pattern):
        """ Return tests from class.  Fake implementation of the load_tests
            protocol from Michael Foord's discover.py.

            loader, tests, and pattern do not do anything, yet
        """
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
    def load_tests(loader, tests, pattern):
        """ Return tests from class.  Fake implementation of the load_tests
            protocol from Michael Foord's discover.py.

            loader, tests, and pattern do not do anything, yet
        """
        return unittest.TestLoader().loadTestsFromTestCase(TestMessageList)

