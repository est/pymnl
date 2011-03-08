#!/usr/bin/python
#
# if_link.py -- constants and data structures from linux/if_link.h
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

from pymnl.attributes import AttrParser

IFLA_IFNAME = 3
IFLA_MTU = 4

class IFLAttrParser(AttrParser):
    """ Parser for interface attributes.
    """
    def __init__(self):
        # dict to hold attributes without an assigned callback
        self._attributes = { 'unmatched': [] }

        self._cb = {IFLA_MTU : self.ifla_mtu,
                    IFLA_IFNAME : self.ifla_ifname}

    def ifla_mtu(self, attr):
        """ Save MTU.

            attr - Attr object
        """
        self._attributes['mtu'] = attr.get_u32()

    def ifla_ifname(self, attr):
        """ Save interface name.

            attr - Attr object
        """
        self._attributes['ifname'] = attr.get_str_stripped()

    def parse(self, data):
        """ Process the attributes.

            data - object with attributes
        """
        for one_attr in self.parse_string(data.get_binary(), offset=0):
            try:
                self._cb[one_attr.get_type()](one_attr)
            except KeyError:
                self._attributes['unmatched'].append(one_attr)

        return self._attributes

