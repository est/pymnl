# attributes.py -- interface to netlink message payload attributes
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

class Attr:
    """ Netlink Length-Type-Value (LTV) attribute:

        |<-- 2 bytes -->|<-- 2 bytes -->|<-- variable -->|
        -------------------------------------------------
        |     length    |      type     |      value     |
        -------------------------------------------------
        |<--------- header ------------>|<-- payload --->|

        The payload of the Netlink message contains sequences of
        attributes that are expressed in LTV format.

        Attr stores the value in packed format, internally.  The value
        is immediately packed when an Attr is created via non-packed data.
        It will be unpacked, as needed, when called for through the
        get_*() methods.
    """
    # pack/unpack format for type and length
    header_format = "hh"

    # various data sizes
    _u8 = 1
    _u16 = 2
    _u32 = 4
    _u64 = 8

    def __init__(self, type=None, value=None, packed_data=None):
        """ Create a new Attr object.

            type - attribute's type (see NLA_* constants in linux/netlink.h)

            value - string or number representing the payload
        """
        if (packed_data):
            # process packed struct into Attr's fields
            (self._length,
             self._type) = unpack(Attr.header_format, packed_data[:4])
            self._value = packed_data[4:]
        else:
            self.set(type, value)


    def __len__(self):
        """ Get the length of the packed attribute (in bytes).
        """
        return calcsize(Attr.header_format) + pymnl.NLA_ALIGN(len(self._value))

    def __getdata__(self):
        """ Return the non-header data string.
        """
        return self._value

    @staticmethod
    def new_u8(type, value):
        """ Return a new one byte long Attr object.
        """
        return Attr(type=type, value=pack("B", value))

    @staticmethod
    def new_u16(type, value):
        """ Return a new two byte long Attr object.
        """
        return Attr(type=type, value=pack("H", value))

    @staticmethod
    def new_u32(type, value):
        """ Return a new four byte long Attr object.
        """
        return Attr(type=type, value=pack("I", value))

    @staticmethod
    def new_u64(type, value):
        """ Return a new eight byte long Attr object.
        """
        return Attr(type=type, value=pack("Q", value))

    @staticmethod
    def new_strnz(type, value):
        """ Return a new Attr object with a non-zero-terminated string.
        """
        return Attr(type=type, value=pack(repr(len(value)) + "s", value))

    @staticmethod
    def new_strz(type, value):
        """ Return a new Attr object with a zero-terminated string.

            This method will add the null termination.  Pass this
            method a non-zero-terminated string.
        """
        value = value + "\x00"
        return Attr.new_strnz(type=type, value=value)

    def set(self, type, value):
        """ Set the attribute type and value.

            type - attribute's type (see NLA_* constants in linux/netlink.h)

            value - string representing the payload
        """
        self._type = type
        self._value = value

    def type(self):
        """ Get the attribute's type.
        """
        return self._type & pymnl.NLA_TYPE_MASK

    def get_u8(self):
        """ Return value as a one byte integer.
        """
        return unpack("B", self._value)[0]

    def get_u16(self):
        """ Return value as a two byte integer.
        """
        return unpack("H", self._value)[0]

    def get_u32(self):
        """ Return value as a four byte integer.
        """
        return unpack("I", self._value)[0]

    def get_u64(self):
        """ Return value as an eight byte integer.
        """
        return unpack("Q", self._value)[0]

    def get_str(self):
        """ Return value as a string.
        """
        return unpack(repr(len(self._value)) + "s", self._value)[0]

    def get_str_stripped(self):
        """ Return value as a string, without zero terminator.
        """
        return self.get_str()[:-1]

    def packed(self):
        """ Return a packed struct to include in message payload.

            Adds null-bytes to end to pad attribute's length to
            a multiple of NLA_ALIGNTO.
        """
        # prepare the header info
        header = pack(Attr.header_format, len(self), self._type)
        # prepare the null padding
        pad = ((len(self) - len(self._value)) * "\x00")
        # push the whole package out
        return header + self._value + pad


class AttrParser:
    """ Base class for attribute parsers.

        This class provides the most basic parsing capability.  In most
        cases, you should use a subclass with callback methods or even
        replace the parse() method.

        However, AttrParser will handle simple attribute data.  And return
        a list of the attributes found.
    """
    def __init__(self, data=None):
        """ Parse a string for netlink attributes.

            data - optional object with attributes
                    The attribute string can be passed here, or sent to
                    the parse() method after initialization.
        """
        # list to hold attributes if no callbacks are assigned
        self._attributes = []
        # dict to hold attribute type to callback method mapping
        self._cb = {}
        if (data):
            self.parse(data)

    def parse_string(self, data, offset=4):
        """ Process the attributes.

            data - raw data to parse

            offset - offset into data at which to start

            This method takes care of the low-level detail of finding
            attributes in a data string and returns individual
            attributes one at a time (parse_string() is a generator).

            Subclasses can override parse() and still use parse_string()
            to retrieve individual attributes from the data.
        """
        index = offset
        while (index < len(data)):
            try:
                attr_length = unpack("h", data[index:index+2])[0]
            except:
                break
            one_attr = Attr(packed_data=data[index:index+attr_length])
            index = index + pymnl.NLA_ALIGN(attr_length)
            yield one_attr

    def parse(self, data):
        """ Process the attributes.

            data - object with attributes
        """
        for one_attr in self.parse_string(data.__getdata__()):
            try:
                self._cb[one_attr.type()](one_attr)
            except KeyError:
                self._attributes.append(one_attr)

        if (len(self._attributes) > 0):
            return self._attributes

    def parse_nested(self, data):
        """ Process nested attributes.

            data - object with attributes
        """
        for one_attr in self.parse_string(data.__getdata__(), 0):
            self._attributes.append(one_attr)

        if (len(self._attributes) > 0):
            return self._attributes

    def get_attrs(self):
        """ Return list of attributes parsed from data string.

              If the data string is passed on object creation, and no
              callback methods have been assigned, this method can be
              used to get the list of attributes.
        """
        return self._attributes



