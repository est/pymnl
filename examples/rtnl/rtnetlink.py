#!/usr/bin/python
#
# rtnetlink.py -- constants and data structures from linux/rtnetlink.h
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

# Route message types
RTM_NEWLINK = 16
RTM_GETLINK = 18
RTM_NEWROUTE = 24
RTM_GETROUTE = 26

class RtGenMessageHeader(object):
    """ A Netlink route generic message header.
    """
    def __init__(self, family=None):
        """ Create a Netlink route generic message header.

            Objects of this type can be used with
            pymnl.message.put_extra_header().

            family - integer - the route message type
        """
        self._format = "B"
        self._family = family

    def set_family(self, family):
        """ Set the route message family.

            family - integer - the route message type
        """
        self._family = family

    def get_family(self):
        """ Returns the route message family.
        """
        return self._family

    def get_binary(self):
        """ Returns a packed struct suitable for sending through a
            netlink socket.

            Raises an exception if family has not been set before calling
            get_binary().
        """
        return pack(self._format, self._family)


