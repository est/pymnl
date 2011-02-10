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

import pymnl
from pymnl.attributes import Attr

# Flags values
NLM_F_REQUEST = 1       # It is a request message.
NLM_F_MULTI = 2         # Multipart message, terminated by NLMSG_DONE
NLM_F_ACK = 4           # Reply with ack, with zero or error code
NLM_F_ECHO = 8          # Echo this request

# Modifiers to GET request
NLM_F_ROOT = 0x100      # specify tree root
NLM_F_MATCH = 0x200     # return all matching
NLM_F_ATOMIC = 0x400    # atomic GET
NLM_F_DUMP = (NLM_F_ROOT|NLM_F_MATCH)

# Modifiers to NEW request
NLM_F_REPLACE = 0x100   # Override existing
NLM_F_EXCL = 0x200      # Do not touch, if it exists
NLM_F_CREATE = 0x400    # Create, if it does not exist
NLM_F_APPEND = 0x800    # Add to end of list

NLMSG_ALIGNTO = 4
NLMSG_ALIGN = pymnl.PYMNL_ALIGN(NLMSG_ALIGNTO)

NLMSG_NOOP = 0x1        # Nothing.
NLMSG_ERROR = 0x2       # Error
NLMSG_DONE = 0x3        # End of a dump
NLMSG_OVERRUN = 0x4     # Data lost

NLMSG_MIN_TYPE = 0x10   # < 0x10: reserved control messages

# pack/unpack format for msg_length, msg_type, msg_flags, msg_seq, pid
header_format = "ihhii"

MSG_HDRLEN = NLMSG_ALIGN(calcsize(header_format))

class Message:
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
        self._msg_length = 0
        self._msg_type = 0
        self._msg_flags = 0
        self._msg_seq = 0
        self._pid = 0
        self._payload = None

        if (buffer):
            (self._msg_length,
             self._msg_type,
             self._msg_flags,
             self._msg_seq,
             self._pid) = unpack(header_format, buffer[:MSG_HDRLEN])

            self._payload = Payload(buffer[NLMSG_ALIGN(MSG_HDRLEN):])

    def __len__(self):
        """ Get the unaligned length of the message (in bytes).
        """
        return MSG_HDRLEN + len(self._payload)

    def get_payload(self):
        """ Return the payload object contained in the message.
        """
        return self._payload

    def add_payload(self, data):
        """ Add payload to the message.

            data - Payload or string
        """
        if (isinstance(data, Payload)):
            self._payload = data
        else:
            self._payload = Payload(data)

    def packed(self):
        """ Return a packed struct for sending to netlink socket.
        """
        if (not self._payload):
            raise UnboundLocalError("payload")

        self._msg_length = NLMSG_ALIGN(MSG_HDRLEN + len(self._payload))

        return pack(header_format,
                    self._msg_length,
                    self._msg_type,
                    self._msg_flags,
                    self._msg_seq,
                    self._pid) + self._payload.__getdata__()


class Payload:
    def __init__(self, contents=None):
        """ The payload of a netlink message.
        """
        if (contents):
            self.set(contents)

    def __len__(self):
        """ Get the length of the payload (in bytes).
        """
        return len(self._contents)

    def __getdata__(self):
        """ Return the non-header data string.
        """
        return self._contents

    def __getitem__(self, index):
        """ Return the value at index.
        """
        return self._contents[index]

    def __repr__(self):
        """ Return escaped data string.
        """
        return repr(self._contents)

    def set(self, contents):
        """ Set the payload contents.

            contents - string representing the payload
        """
        self._contents = contents
        self._format = repr(NLMSG_ALIGN(len(self._contents))) + "s"

    def format(self):
        """ Get the payload's struct format.
        """
        return self._format

    def add_attr(self, attribute):
        """ Add an Attr object to the payload.

            attribute - an Attr object
        """
        self.set(self._contents + attribute.packed())











