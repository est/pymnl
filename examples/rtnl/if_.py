#!/usr/bin/python
#
# if_.py -- constants and data structures from net/if.h
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

from struct import calcsize, pack, unpack

IFF_UP = 0x1          # interface is up
IFF_RUNNING = 0x40

class IfInfoMessage(object):
    """ Passes link level specific information, not dependent on network
        protocol. -- /usr/include/linux/rtnetlink.h
    """
    def __init__(self, contents=None):
        """
        """
        self._format = "BBHiII"
        self.family = 0
        self.pad = 0
        self.type_ = 0
        self.index = 0
        self.flags = 0
        self.change = 0
        if (contents):
            contents = contents[:calcsize(self._format)]
            (self.family,
             self.pad,
             self.type_,
             self.index,
             self.flags,
             self.change) = unpack(self._format, contents)

    def __len__(self):
        """
        """
        return calcsize(self._format)

    def get_binary(self):
        """
        """
        return pack(self._format, self.family, self.pad, self.type_,
                        self.index, self.flags, self.change)

