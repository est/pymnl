# message.py -- interface to netlink messages
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

from struct import calcsize, pack, unpack

class Message:
    header_format = "ihhii"

    def __init__(self, buffer=None):
        """ A netlink message.

            Netlink message:

            |<----------------- 4 bytes ------------------->|
            |<----- 2 bytes ------>|<------- 2 bytes ------>|
            |-----------------------------------------------|
            |      Message length (including header)        |
            |-----------------------------------------------|
            |     Message type     |     Message flags      |
            |-----------------------------------------------|
            |           Message sequence number             |
            |-----------------------------------------------|
            |                 Netlink PortID                |
            |-----------------------------------------------|
            |                                               |
            .                   Payload                     .
            |_______________________________________________|

            There is usually an extra header after the the Netlink header
            (at the beginning of the payload). This extra header is specific
            of the Netlink subsystem. After this extra header, it comes the
            sequence of attributes that are expressed in
            Type-Length-Value (TLV) format.
        """
        self.msg_length = 0
        self.msg_type = 0
        self.msg_flags = 0
        self.msg_seq = 0
        self.pid = 0
        self.payload = None

        if (buffer):
            payload_size = len(buffer) - calcsize(Message.header_format)

            (self.msg_length,
            self.msg_type,
            self.msg_flags,
            self.msg_seq,
            self.pid,
            self.payload) = unpack(Message.header_format +
                                    repr(payload_size) + "s", buffer)

    def packed(self):
        """ Return a packed struct for sending to netlink socket.
        """
        if (not self.payload):
            raise UnboundLocalError("payload")

        self.msg_length = calcsize(Message.header_format) + len(self.payload)

        return pack(Message.header_format + repr(len(self.payload)) + "s",
                self.msg_length,
                self.msg_type,
                self.msg_flags,
                self.msg_seq,
                self.pid,
                self.payload)


class Payload:
    def __init__(self, contents=None):
        """ The payload of a netlink message.
        """
        if (contents):
            self._contents = contents
            self._format = repr(len(self._contents)) + "s"

