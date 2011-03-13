#!/usr/bin/python
#
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

import os
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

class Message(object):
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
            of the Netlink subsystem. After this extra header, comes the
            sequence of attributes that are expressed in
            Length-Type-Value (LTV) format.
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
        if (self._payload):
            return MSG_HDRLEN + len(self._payload)
        else:
            return MSG_HDRLEN

    def put_extra_header(self, header):
        """ Add a header before the Payload.

            header - The object which contains the extra header.  This
                        object must provide a get_binary() method which
                        returns a binary string/bytes with the netlink
                        data, like Payload or GenlMessageHeader.
        """
        if (self._payload):
            self._payload = Payload(header.get_binary() +
                                    self._payload.get_binary())
        else:
            self._payload = Payload(header.get_binary())

    def set_type(self, type_):
        """ Sets the message type.

            type_ - 2-byte integer
        """
        if ((type_ & 0xffff) != type_):
            raise ValueError("Message type must be between 0 and " + \
                                "65535, inclusive.")
        self._msg_type = type_

    def get_type(self):
        """ Returns the 2-byte type.
        """
        return self._msg_type

    def set_flags(self, flags_):
        """ Sets the message flags.

            flags_ - 2-byte integer
        """
        if ((flags_ & 0xffff) != flags_):
            raise ValueError("Message flags must be between 0 and " + \
                                "65535, inclusive.")
        self._msg_flags = flags_

    def get_flags(self):
        """ Returns the 2-byte flag.
        """
        return self._msg_flags

    def set_seq(self, seq_):
        """ Sets the message sequence number.

            seq_ - 4-byte integer
        """
        if ((seq_ & 0xffffffff) != seq_):
            raise ValueError("Message sequence number must be " + \
                                "between 0 and 4294967295, inclusive.")
        self._msg_seq = seq_

    def get_seq(self):
        """ Returns the 4-byte sequence number.
        """
        return self._msg_seq

    def set_portid(self, pid_):
        """ Sets the message port id.

            pid_ - 4-byte integer
        """
        if ((pid_ & 0xffffffff) != pid_):
            raise ValueError("Message port id must be between 0 and " + \
                                "4294967295, inclusive.")
        self._pid = pid_

    def get_portid(self):
        """ Returns the 4-byte port id.
        """
        return self._pid

    def add_payload(self, data):
        """ Add payload to the message.

            data - Payload or string
        """
        if (not isinstance(data, Payload)):
            data = Payload(data)
        if (self._payload):
            self._payload = Payload(self._payload.get_binary() +
                                        data.get_binary())
        else:
            self._payload = data

    def get_payload(self):
        """ Return the payload object contained in the message.
        """
        return self._payload

    def ok(self):
        """ Check that Message is internally consistent. (i.e. verify that
            a netlink message is not malformed nor truncated.
        """
        return len(self) >= MSG_HDRLEN

    def seq_ok(self, seq):
        """ Perform sequence tracking.

            seq - last sequence number used to send a message

            This method returns true if the sequence tracking is
            fulfilled, otherwise false is returned. We skip the tracking
            for netlink messages whose sequence number is zero since it is
            usually reserved for event-based kernel notifications. On the
            other hand, if seq is set but the message sequence number is
            not set (i.e. this is an event message coming from
            kernel-space), then we also skip the tracking. This approach is
            good if we use the same socket to send commands to kernel-space
            (that we want to track) and to listen to events (that we do not
            track).
        """
        match = True
        if (seq):
            match = (self._msg_seq == seq)
        return (self._msg_seq and match)

    def portid_ok(self, portid):
        """ Perform portID origin check.

            portid - netlink portid that we want to check

            This method returns true if the origin is fulfilled, otherwise
            false is returned. We skip the tracking for netlink message
            whose portID is zero since it is reserved for event-based
            kernel notifications. On the other hand, if portid is set but
            the message PortID is not (i.e. this is an event message coming
            from kernel-space), then we also skip the tracking. This
            approach is good if we use the same socket to send commands to
            kernel-space (that we want to track) and to listen to events
            (that we do not track).
        """
        match = True
        if (portid):
            match = (self._pid == portid)
        return (self._pid and match)

    def printf_header(self):
        """ This method prints the netlink message header to stdout.
            It may be useful for debugging purposes.  Use Message.printf()
            to print out a full message.

            One example of the output is the following:

            ----------------        ------------------
            |  0000000040  |        | message length |
            | 00016 | R-A- |        |  type | flags  |
            |  1289148991  |        | sequence number|
            |  0000000000  |        |     port ID    |
            ----------------        ------------------

            This example shows the header of the netlink message that
            is sent to kernel-space to set up the link interface eth0.  The
            netlink header data is displayed in base 10.   The possible
            flags in the netlink header are:

                - R, that indicates that NLM_F_REQUEST is set.
                - M, that indicates that NLM_F_MULTI is set.
                - A, that indicates that NLM_F_ACK is set.
                - E, that indicates that NLM_F_ECHO is set.

            The lack of one flag is displayed with '-'.
        """
        request = "-"
        if (self._msg_flags & NLM_F_REQUEST):
            request = "R"
        multi = "-"
        if (self._msg_flags & NLM_F_MULTI):
            multi = "M"
        ack = "-"
        if (self._msg_flags & NLM_F_ACK):
            ack = "A"
        echo = "-"
        if (self._msg_flags & NLM_F_ECHO):
            echo = "E"
        print("----------------\t------------------");
        print("|  %.010u  |\t| message length |" % len(self));
        print("| %.05u | %c%c%c%c |\t|  type | flags  |" %
            (self._msg_type,
            request, multi, ack, echo))
        print("|  %.010u  |\t| sequence number|" % self._msg_seq);
        print("|  %.010u  |\t|     port ID    |" % self._pid);
        print("----------------\t------------------");

    def printf(self, extra_header_size=0):
        """ This method prints the full netlink message to stdout.
            It may be useful for debugging purposes.

            It calls Message.printf_header() and Payload.printf() to do
            the real work.
        """
        self.printf_header()
        self._payload.printf(self._msg_type, extra_header_size)

    def get_binary(self):
        """ Return a packed struct suitable for sending through a
            netlink socket.
        """
        if (not self._payload):
            raise UnboundLocalError("There is no payload in this message")

        self._msg_length = NLMSG_ALIGN(MSG_HDRLEN + len(self._payload))

        return pack(header_format,
                    self._msg_length,
                    self._msg_type,
                    self._msg_flags,
                    self._msg_seq,
                    self._pid) + self._payload.get_binary()

    def get_errno(self):
        """ Return the errno reported by Netlink.
        """
        errno_ = 0
        if (self._msg_type == NLMSG_ERROR):
            # The error code is a signed integer stored in the
            #   first four bytes of the payload
            errno_ = unpack("i", self._payload.get_data()[:4])[0]
            # "Netlink subsystems returns the errno value
            #   with different signess" -- libmnl/src/callback.c
            if (errno_ < 0):
                errno_ = -1 * errno_
        return errno_

    def get_errstr(self):
        """ Return the errno reported by Netlink as
            interpretted by os.strerror.
        """
        return os.strerror(self.get_errno())


class Payload(object):
    def __init__(self, contents=None):
        """ The payload of a netlink message.

            contents - string or object representing the payload
                        When passing an object, it must implement the
                        get_binary() method.
        """
        if (contents):
            self.set(contents)
        else:
            self._contents = b''

    def __len__(self):
        """ Get the length of the payload (in bytes).
        """
        return len(self._contents)

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

            contents - string or object representing the payload
                        When passing an object, it must implement the
                        get_binary() method.
        """
        if (isinstance(contents, str) or isinstance(contents, bytes)):
            # Py2, it's a str; Py3, it's a bytes
            self._contents = contents
        else:
            self._contents = contents.get_binary()
        self._format = repr(NLMSG_ALIGN(len(self._contents))) + "s"

    def format(self):
        """ Get the payload's struct format.
        """
        return self._format

    def printf(self, msg_type, extra_header_size):
        """ This method prints the netlink message payload to stdout.
            It may be useful for debugging purposes.  Use Message.printf()
            to print out a full message.

            One example of the output is the following:

            | 00 00 00 00  |        |  extra header  |
            | 00 00 00 00  |        |  extra header  |
            | 01 00 00 00  |        |  extra header  |
            | 01 00 00 00  |        |  extra header  |
            |00008|--|00003|        |len |flags| type|
            | 65 74 68 30  |        |      data      |       e t h 0
            ----------------        ------------------

            This example shows the payload for the netlink message
            that is send to kernel-space to set up the link interface eth0.
            The extra header and the attribute payloads are expressed in
            base 16.

            The attribute header is shown in base 10. The possible flags in
            the attribute header are:

                - N, that indicates that NLA_F_NESTED is set.
                - B, that indicates that NLA_F_NET_BYTEORDER is set.

            The lack of one flag is displayed with '-'.
        """
        rem = 0
        for index in range(0, len(self), 4):
            # get four bytes of payload for later use
            buf = []
            for char in self._contents[index:index+4]:
                try:
                    # make sure we have a list of numbers, needed in Py2
                    buf.append(ord(char))
                except TypeError:
                    # char is already a number, we're probably in Py3
                    buf.append(char)

            # make a stunted Attr so we can test its attribute-ness later
            one_attr = Attr(packed_data=self._contents[index:index+4])

            if (msg_type < NLMSG_MIN_TYPE):
                # netlink control message
                print("| %.2x %.2x %.2x %.2x  |\t|                |" %
                    (0xff & buf[0],  0xff & buf[1],
                     0xff & buf[2],  0xff & buf[3]))
            elif (extra_header_size > 0):
                # special handling for the extra header
                extra_header_size = extra_header_size - 4
                print("| %.2x %.2x %.2x %.2x  |\t|  extra header  |" %
                    (0xff & buf[0],  0xff & buf[1],
                     0xff & buf[2],  0xff & buf[3]))
            elif ((rem == 0) and (one_attr.get_type() != 0)):
                # this seems like an attribute header
                # Since this looks like an attribute, make a full Attr
                #   with which to work.
                one_attr = Attr(packed_data=self._contents[index:index+one_attr._length])
                line = "|%c[%d;%dm" % (27, 1, 31)
                line = line + "%.5u" % (len(one_attr),)
                line = line + "%c[%dm" % (27, 0)
                line = line + "|"
                line = line + "%c[%d;%dm" % (27, 1, 32)
                nest = "-"
                if (one_attr.is_nested()):
                    nest = "N"
                byteorder = "-"
                if (one_attr.get_type() & pymnl.attributes.NLA_F_NET_BYTEORDER):
                    byteorder = "B"
                line = line + "%c%c" % (nest, byteorder)
                line = line + "%c[%dm" % (27, 0)
                line = line + "|"
                line = line + "%c[%d;%dm" % (27, 1, 34)
                line = line + "%.5u" % (one_attr.get_type(),)
                line = line + "%c[%dm|\t" % (27, 0)
                line = line + "|len |flags| type|"
                print(line)
                if (not one_attr.is_nested()):
                    rem = len(one_attr) - calcsize(pymnl.attributes.header_format)
            elif (rem > 0):
                # this is the attribute payload
                rem = rem - 4;
                line = ("| %.2x %.2x %.2x %.2x  |\t" %
                    (0xff & buf[0],  0xff & buf[1],
                     0xff & buf[2],  0xff & buf[3]))
                line = line + "|      data      |"
                for bindex in range(0, 4):
                    # Convert each value to a string for testing.
                    # Yes, this is the same value we converted into an
                    # integer above.  But that was for Py2 and this is
                    # needed for Py3.  So, we convert and test the 4
                    # buffer bytes for both Py2 and Py3.  This way, the
                    # bitwise ops work above and the isalnum()
                    # test works here.
                    if (not chr(buf[bindex]).isalnum()):
                        buf[bindex] = 0
                line = line + ("\t %c %c %c %c" %
                    (buf[0], buf[1], buf[2], buf[3]))
                print(line)
        print("----------------\t------------------");

    def add_attr(self, attribute):
        """ Add an Attr object to the payload.

            attribute - an Attr object
        """
        self.set(self._contents + attribute.get_binary())

    def get_binary(self):
        """ Return a packed struct suitable for sending through a
            netlink socket.
        """
        # prepare the null padding
        pad = (NLMSG_ALIGN(len(self)) - len(self)) * b'\x00'
        # push the whole package out
        return self._contents + pad

    def get_data(self):
        """ Return the non-header data string.  This is the non-aligned
            version of get_binary().
        """
        return self._contents


class MessageList(list):
    def __init__(self, msg):
        """ Holds the Message objects making up a multipart message.
        """
        if (msg):
            if (isinstance(msg, Message)):
                self.append(msg)
            elif (isinstance(msg, str) or isinstance(msg, bytes)):
                # Py2, it's a str; Py3, it's a bytes
                self.split(msg)
            else:
                raise TypeError("MessageList only accepts Messages " +
                                "or a packed string")

    def size(self):
        """ Return the length (in bytes) of the total MessageList.
        """
        length = 0
        for msg in self:
            length = length + len(msg)
        return length

    def split(self, msg):
        """ Split multipart message into its component messages.
        """
        while (msg):
            one_msg = Message(msg)
            # Is more data than message header calls for available?
            if (len(one_msg) > one_msg._msg_length):
                # make a Message from the right amount of data
                self.append(Message(msg[:one_msg._msg_length]))
                # strip off the data used to make previous Message
                msg = msg[one_msg._msg_length:]
            else:
                self.append(one_msg)
                msg = None







