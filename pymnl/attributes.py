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
    """
    # pack/unpack format for type and length
    header_format = "hh"


    def __init__(self, type=None, value=None, size=None, packed_data=None):
        """ Create a new Attr object.

            type - attribute's type (see NLA_* constants in linux/netlink.h)

            value - string or number representing the payload

            size - the length (in bytes) of the value
                    - size of a _u8 is one byte
                    - size of a _u16 is two bytes
                    - size of a _u32 is four bytes
                    - size of a _u64 is eight bytes
                    - size of a strnz is one byte per character in string
                    - size of a strz is one byte per character
                        in string, plus for terminating zero
        """
        if (packed_data):
            # process packed struct into Attr's fields
            (self._length,
             self._type) = unpack(Attr.header_format, packed_data[:4])
            self._value = packed_data[4:]
            self._size = len(self._value)
        else:
            self.set(type, value, size)


    def __len__(self):
        """ Get the length of the attribute (in bytes).
        """
        return calcsize(Attr.header_format) + len(self._value)

    def set(self, type, value, size):
        """ Set the attribute type and value.

            type - attribute's type (see NLA_* constants in linux/netlink.h)

            value - string representing the payload

            size - the length (in bytes) of the value (see __init__())
        """
        self._type = type
        self._value = value
        self._size = size

    def type(self):
        """ Get the attribute's type.
        """
        return self._type & pymnl.NLA_TYPE_MASK

    def value(self):
        """ Get the attribute's value.
        """
        return self._value

    def format(self):
        """ Get the attribute's struct format.
        """
        return Attr.header_format + self._value_format




