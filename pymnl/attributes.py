#!/usr/bin/python
#
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

# Forward compatibility with Py3k
# copied from http://wiki.python.org/moin/PortingPythonToPy3k
try:
    bytes
except NameError:
    bytes = str


# netlink attributes
#
#  nla_type (16 bits)
#  +---+---+-------------------------------+
#  | N | O | Attribute Type                |
#  +---+---+-------------------------------+
#  N:=Carries nested attributes
#  O:=Payload stored in network byte order
#
#  Note:The N and O flag are mutually exclusive.
#
NLA_F_NESTED = (1 << 15)
NLA_F_NET_BYTEORDER = (1 << 14)
NLA_TYPE_MASK = ~(NLA_F_NESTED | NLA_F_NET_BYTEORDER)

NLA_ALIGNTO = 4
NLA_ALIGN = pymnl.PYMNL_ALIGN(NLA_ALIGNTO)

# pack/unpack format for type and length
header_format = "hh"

ATTR_HDRLEN = NLA_ALIGN(calcsize(header_format))

# minimal netlink attribute types
TYPE_UNSPEC = 0         # Unspecified type
TYPE_U8 = 1             # 8bit integer
TYPE_U16 = 2            # 16bit integer
TYPE_U32 = 3            # 32bit integer
TYPE_U64 = 4            # 64bit integer
TYPE_STRING = 5         # character string
TYPE_FLAG = 6           # flag
TYPE_MSECS = 7          # micro seconds (64bit)
TYPE_NESTED = 8         # nested attributes
TYPE_NESTED_COMPAT = 9
TYPE_NUL_STRING = 10    # null-terminated character string
TYPE_BINARY = 11
TYPE_MAX = 12           # always keep last

# various data type sizes
_u8 = calcsize("B")
_u16 = calcsize("H")
_u32 = calcsize("I")
_u64 = calcsize("Q")


class Attr(object):
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
    def __init__(self, type=None, value=None, packed_data=None):
        """ Create a new Attr object.

            type - attribute's type (see NLA_* constants in linux/netlink.h)

            value - string or number representing the payload

            packed_data - This is the binary string containing the
                attribute data.  This could be the output from another
                object's get_binary() method or data directly from Netlink.
        """
        if (packed_data):
            # process packed struct into Attr's fields
            (self._length,
             self._type) = unpack(header_format, packed_data[:4])
            self._value = packed_data[4:]
        else:
            self.set(type, value)


    def __len__(self):
        """ Get the length of the packed attribute (in bytes).
        """
        return ATTR_HDRLEN + NLA_ALIGN(self.get_value_len())

    def get_value_len(self):
        """ Return the length of the data payload.
        """
        return len(self._value)

    @staticmethod
    def new_u8(type, value):
        """ Return a new one byte long Attr object.
        """
        if ((value < 0) or (value > pow(2, 8))):
            raise TypeError
        return Attr(type=type, value=pack("B", value))

    @staticmethod
    def new_u16(type, value):
        """ Return a new two byte long Attr object.
        """
        if ((value < 0) or (value > pow(2, 16))):
            raise TypeError
        return Attr(type=type, value=pack("H", value))

    @staticmethod
    def new_u32(type, value):
        """ Return a new four byte long Attr object.
        """
        if ((value < 0) or (value > pow(2, 32))):
            raise TypeError
        return Attr(type=type, value=pack("I", value))

    @staticmethod
    def new_u64(type, value):
        """ Return a new eight byte long Attr object.
        """
        if ((value < 0) or (value > pow(2, 64))):
            raise TypeError
        return Attr(type=type, value=pack("Q", value))

    @staticmethod
    def new_strnz(type, value):
        """ Return a new Attr object with a non-zero-terminated string.
        """
        if (not isinstance(value, bytes)):
            raise TypeError
        return Attr(type=type, value=pack(repr(len(value)) + "s", value))

    @staticmethod
    def new_strz(type, value):
        """ Return a new Attr object with a zero-terminated string.

            This method will add the null termination.  Pass this
            method a non-zero-terminated string.
        """
        if (not isinstance(value, bytes)):
            raise TypeError
        value = value + b'\x00'
        return Attr.new_strnz(type=type, value=value)

    def set(self, type, value):
        """ Set the attribute type and value.

            type - attribute's type (see NLA_* constants in linux/netlink.h)

            value - string representing the payload
        """
        self._type = type
        self._value = value

    def get_type(self):
        """ Get the attribute's type.
        """
        return self._type & NLA_TYPE_MASK

    def type_valid(self):
        """ Return False if the type is not known, otherwise return True.
        """
        if (self.get_type() > TYPE_MAX):
            return False
        return True

    def get_u8(self):
        """ Return value as a one byte integer.

            Raises TypeError if the data length does not match
            the length expected for the type.
        """
        if (self.get_type() == TYPE_U8 and self.get_value_len() != _u8):
            raise TypeError("Integer attribute is too short")
        return unpack("B", self._value)[0]

    def get_u16(self):
        """ Return value as a two byte integer.

            Raises TypeError if the data length does not match
            the length expected for the type.
        """
        if (self.get_type() == TYPE_U16 and self.get_value_len() != _u16):
            raise TypeError("Integer attribute is too short")
        return unpack("H", self._value)[0]

    def get_u32(self):
        """ Return value as a four byte integer.

            Raises TypeError if the data length does not match
            the length expected for the type.
        """
        if (self.get_type() == TYPE_U32 and self.get_value_len() != _u32):
            raise TypeError("Integer attribute is too short")
        return unpack("I", self._value)[0]

    def get_u64(self):
        """ Return value as an eight byte integer.

            Raises TypeError if the data length does not match
            the length expected for the type.
        """
        if (self.get_type() == TYPE_U64 and self.get_value_len() != _u64):
            raise TypeError("Integer attribute is too short")
        return unpack("Q", self._value)[0]

    def get_str(self):
        """ Return value as a string.

            Raises TypeError if the data length is zero or is
            not null-terminated.  A null-terminated string
            should have a non-zero length and a null termination
            or something went wrong.
        """
        if (type == TYPE_NUL_STRING):
            if (self.get_value_len() == 0):
                raise TypeError("String attribute is too short")
            if (self._value[-1:] != 0):
                raise TypeError("This attribute is not null-terminated," +
                                "as it claims to be")
        return unpack(repr(len(self._value)) + "s", self._value)[0]

    def get_str_stripped(self):
        """ Return value as a string, without zero terminator.

            Raises TypeError if the data length is zero.
            A string should have a non-zero length or something went wrong.
        """
        if (type == TYPE_STRING and self.get_value_len() == 0):
            raise TypeError("String attribute is too short")
        string_ = self.get_str()
        if ((string_[-1] == b'\x00') or (string_[-1] == 0)):
            # b'\x00' works in Py2, but 0 works in Py3, gah!
            string_ = string_[:-1]
        return string_

    def get_binary(self):
        """ Return a packed struct to include in message payload.

            Adds null-bytes to end to pad attribute's length to
            a multiple of NLA_ALIGNTO.
        """
        # prepare the header info
        header = pack(header_format, len(self), self._type)
        # prepare the null padding
        pad = (NLA_ALIGN(len(self._value)) - self.get_value_len()) * b'\x00'
        # push the whole package out
        return header + self._value + pad

    def get_data(self):
        """ Return the non-header data string, a.k.a. the attribute's
            payload (not it's Payload).
        """
        return self._value

    def toggle_nested(self):
        """ Toggle the nested flag on and off for the Attr object.
        """
        self._type = self._type ^ NLA_F_NESTED

    def is_nested(self):
        """ Return True if the nested flag is set, else return False.
        """
        return self._type & NLA_F_NESTED


class AttrParser(object):
    """ Base class for attribute parsers.

        This class provides the most basic parsing capability.  In most
        cases, you should use a subclass with callback methods or even
        replace the parse() method.

        However, AttrParser will handle simple attribute data.  And return
        a list of the attributes found.
    """
    def __init__(self, data_obj=None):
        """ Parse a string for netlink attributes.

            data_obj - An optional object with attributes.  The data
                object can be passed here and will be immediately parsed.
                Or the object can be sent to the parse() method after
                initialization.  See parse() for more details.
        """
        # list to hold attributes if no callbacks are assigned
        self._attributes = []
        # dict to hold attribute type to callback method mapping
        self._cb = {}
        if (data_obj):
            self._attributes = self.parse(data_obj)

    def parse_string(self, data, offset=0):
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
                attr_length = unpack("H", data[index:index+2])[0]
            except:
                break
            end_index = index + attr_length
            one_attr = Attr(packed_data=data[index:end_index])
            index = NLA_ALIGN(end_index)
            yield one_attr

    def parse(self, data_obj):
        """ Returns a list of Attr processed from the binary string.

            data_obj - An object containing attributes and providing the
                get_binary() method.  See Message and Payload for examples
                of get_binary().
        """
        attributes = []
        for one_attr in self.parse_string(data_obj.get_binary()):
            try:
                self._cb[one_attr.get_type()](one_attr)
            except KeyError:
                attributes.append(one_attr)
        if (len(attributes) > 0):
            return attributes

    def parse_nested(self, data_obj):
        """ Returns a list of Attr processed from the binary string.

            data_obj - An object containing nested attributes and providing
                the get_data() method.  get_data() must return the non-header
                binary string to be parsed here.  See Payload and Attr
                for examples of get_data().
        """
        attributes = []
        for one_attr in self.parse_string(data_obj.get_data(), 0):
            attributes.append(one_attr)
        if (len(attributes) > 0):
            return attributes

    def get_attrs(self):
        """ Return list of attributes parsed from data string.

              If the data string is passed on object creation, and no
              callback methods have been assigned, this method can be
              used to get the list of attributes.
        """
        return self._attributes

