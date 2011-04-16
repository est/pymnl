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

from random import randint
import socket
from struct import pack
import unittest

import pymnl
from pymnl.nlsocket import *

from pymnl.message import Message, MessageList, Payload


class TestSocket(unittest.TestCase):

    def setUp(self):
        """ Set up conditions necessary for each test.
        """
        self.nl_socket = Socket(pymnl.NETLINK_GENERIC)
        self._pid = randint(1, pow(2, 31))
        self._groups = 0
        self.nl_socket.bind(self._pid, self._groups)

    def test_bus(self):
        """ Test that the requested bus is the actual bus.
        """
        self.assertEqual(self.nl_socket._bus, pymnl.NETLINK_GENERIC,
            "Netlink socket bus did not match")

    def test_pid(self):
        """ Test that the requested port id is the actual port id.
        """
        self.assertEqual(self.nl_socket.get_portid(), self._pid,
            "Netlink socket port id did not match")

    def test_groups(self):
        """ Test that the requested groups is the actual groups.
        """
        self.assertEqual(self.nl_socket.get_groups(), self._groups,
            "Netlink socket multicast groups did not match")

    def test_send_recv(self):
        """ Test sending and receiving a Netlink message.
        """
        # build a Message to send through the socket
        msg = Message()
        msg.set_type(16)
        msg.set_flags(5)
        msg.set_seq(randint(1, pow(2, 31)))
        msg.set_portid(self._pid)
        msg.add_payload(Payload(pack("BBH", 3, 1, 0)))
        # send and receive Message through a fake socket
        self.nl_socket._socket = MockSocket()
        self.nl_socket.send(msg)
        # save first Message from returned MessageList
        recv_msg = self.nl_socket.recv()[0]
        self.assertEqual(msg.get_binary(), recv_msg.get_binary())

    def test_get_sock(self):
        """ Test that the underlying socket can be retrieved.
        """
        self.assertTrue(isinstance(self.nl_socket.get_sock(), socket.socket),
            "object returned by get_sock() was not a socket")

    def test_sock_options(self):
        """ Test that socket options can be set and retrieved.
        """
        initial_sock_opt = self.nl_socket.getsockopt(NETLINK_NO_ENOBUFS)
        # set the socket option to its opposite
        self.nl_socket.setsockopt(NETLINK_NO_ENOBUFS, initial_sock_opt ^ 1)
        middle_sock_opt = self.nl_socket.getsockopt(NETLINK_NO_ENOBUFS)
        self.assertNotEqual(initial_sock_opt, middle_sock_opt,
            "Netlink socket option matched when it should NOT")
        # set the socket option to its opposite (toggle to original value)
        self.nl_socket.setsockopt(NETLINK_NO_ENOBUFS, middle_sock_opt ^ 1)
        final_sock_opt = self.nl_socket.getsockopt(NETLINK_NO_ENOBUFS)
        self.assertEqual(initial_sock_opt, final_sock_opt,
            "Netlink socket option did not matched")

    def tearDown(self):
        """ Clean up after each test.
        """
        self.nl_socket.close()

    @staticmethod
    def load_tests(loader, tests, pattern):
        """ Return tests from class.  Fake implementation of the load_tests
            protocol from Michael Foord's discover.py.

            loader, tests, and pattern do not do anything, yet
        """
        return unittest.TestLoader().loadTestsFromTestCase(TestSocket)


class MockSocket(object):
    def send(self, nl_message):
        """ Pretend to send a message, instead, save it.
        """
        self._message = nl_message

    def recv(self, bufsize, flags):
        """ Return the saved message.
        """
        return self._message

    def close(self):
        """ Fake the closing of the socket.
        """
        pass

