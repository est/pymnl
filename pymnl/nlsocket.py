#!/usr/bin/python
#
# nlsocket.py -- interface to netlink socket
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
# Much of the method docstrings are from libmnl and are
#      Copyright 2008-2010 by Pablo Neira Ayuso <pablo@netfilter.org>
#

from resource import getpagesize
import socket

import pymnl
from pymnl.message import MessageList

NETLINK_ADD_MEMBERSHIP = 1
NETLINK_DROP_MEMBERSHIP = 2
NETLINK_PKTINFO = 3
NETLINK_BROADCAST_ERROR = 4
NETLINK_NO_ENOBUFS = 5

#
# libmnl.h
#

SOL_NETLINK = 270

SOCKET_AUTOPID = 0

SOCKET_BUFFER_SIZE = 8192
if (getpagesize() < 8192):
    SOCKET_BUFFER_SIZE = getpagesize()


class Socket(object):
    def __init__(self, bus):
        """ A netlink socket.

            bus - the netlink socket bus ID
                    (see NETLINK_* constants in linux/netlink.h)

            Raises an exception on error.
        """
        self._bus = bus
        self._groups = 0   # multicast groups mask

        self._socket = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, bus)

    def get_sock(self):
        """ Get the underlying socket object.

            This is useful if you need to set non-netlink socket options.
        """
        return self._socket

    def get_portid(self):
        """ Obtain netlink PortID from netlink socket.

            This method returns the netlink PortID of this netlink socket.
            It's a common mistake to assume that this PortID equals the
            process ID which is not always true. This is the case if you
            open more than one socket that is binded to the same netlink
            subsystem from the same process.
        """
        return self._socket.getsockname()[0]

    def get_groups(self):
        """ Obtain netlink groups from netlink socket.
        """
        return self._socket.getsockname()[1]

    def bind(self, pid=SOCKET_AUTOPID, groups=0):
        """ Bind netlink socket.

            pid - The port ID you want to use.  You can use
                    SOCKET_AUTOPID (which is 0) for automatic port ID
                    selection.

            groups - the group of message you're interested in

            Raises an exception on error.
        """
        self._socket.bind((pid, groups))

    def send(self, nl_message):
        """ Send a netlink message.

            nl_message - the netlink message to be sent

            Raises an exception on error. Otherwise, it returns the number of
            bytes sent.
        """
        return self._socket.send(nl_message.get_binary())

    def recv(self, bufsize=SOCKET_BUFFER_SIZE, flags=0):
        """ Receive a netlink message.

            bufsize - max data to receive
                        Use SOCKET_BUFFER_SIZE (which is 8KB, see
                        linux/netlink.h for more information). Using this
                        buffer size ensures that your buffer is big enough
                        to store the netlink message without truncating it.

            flags - see socket.recv()

            Raises an exception on error.  Otherwise, it returns a
            MessageList.
        """
        return MessageList(self._socket.recv(bufsize, flags))

    def close(self):
        """ Close the socket.
        """
        self._socket.close()
        self._bus = None

    def setsockopt(self, optname, value):
        """ Set Netlink socket option.

            optname - option to set

            value - value to set for the option

            This method allows you to set some Netlink socket options. As
            of this writing (see linux/netlink.h), the existing options are:

                - NETLINK_ADD_MEMBERSHIP

                - NETLINK_DROP_MEMBERSHIP

                - NETLINK_PKTINFO

                - NETLINK_BROADCAST_ERROR

                - NETLINK_NO_ENOBUFS

            In the early days, Netlink only supported 32 groups expressed
            in a 32-bits mask. However, since 2.6.14, Netlink may have up
            to 2^32 multicast groups but you have to use setsockopt() with
            NETLINK_ADD_MEMBERSHIP to join a given multicast group. This
            method internally calls setsockopt() to join a given netlink
            multicast group. You can still use Socket.bind() and the 32-bit
            mask to join a set of Netlink multicast groups.

            See Python's socket module for more information about value.
        """
        self._socket.setsockopt(SOL_NETLINK, optname, value)

    def getsockopt(self, optname, buflen=None):
        """ Get a Netlink socket option.

            optname - the option to get

            buflen - optional (see Python's socket module)
        """
        self._socket.getsockopt(SOL_NETLINK, optname, buflen)

