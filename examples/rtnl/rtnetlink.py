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


# rtm_type
RTN_UNSPEC = 0
RTN_UNICAST = 1
RTN_LOCAL = 2
RTN_BROADCAST = 3
RTN_ANYCAST = 4
RTN_MULTICAST = 5
RTN_BLACKHOLE = 6
RTN_UNREACHABLE = 7
RTN_PROHIBIT = 8
RTN_THROW = 9
RTN_NAT = 10
RTN_XRESOLVE = 11
__RTN_MAX = 12

# rtm_protocol
RTPROT_UNSPEC = 0
RTPROT_REDIRECT = 1
RTPROT_KERNEL = 2   # route installed by kernel
RTPROT_BOOT = 3     # route installed during boot
RTPROT_STATIC = 4   # route installed by administrator
# Values >= RTPROT_STATIC are not interpreted by kernel, they are
# just user-defined.

# rtm_scope
#
# Really it is not scope, but sort of distance to the destination.
# NOWHERE are reserved for not existing destinations, HOST is our
# local addresses, LINK are destinations, located on directly attached
# link and UNIVERSE is everywhere in the Universe.
#
# Intermediate values are also possible f.e. interior routes
# could be assigned a value between UNIVERSE and LINK.
RT_SCOPE_UNIVERSE = 0     # everywhere in the universe
#    ... user defined values ...
RT_SCOPE_SITE = 200
RT_SCOPE_LINK = 253       # destination attached to link
RT_SCOPE_HOST = 254       # local address
RT_SCOPE_NOWHERE  = 255   # not existing destination

# rtm_flags
RTM_F_NOTIFY = 0x100    # notify user of route change
RTM_F_CLONED = 0x200    # this route is cloned
RTM_F_EQUALIZE = 0x400  # Multipath equalizer: NI
RTM_F_PREFIX = 0x800    # Prefix addresses

# Reserved table identifiers
RT_TABLE_UNSPEC = 0
# ... user defined values ...
RT_TABLE_COMPAT = 252
RT_TABLE_DEFAULT = 253
RT_TABLE_MAIN = 254
RT_TABLE_LOCAL = 255
RT_TABLE_MAX = 0xFFFFFFFF
# Synonimous attribute: RTA_TABLE.

# Routing message attributes
RTA_UNSPEC = 0
RTA_DST = 1
RTA_SRC = 2
RTA_IIF = 3
RTA_OIF = 4
RTA_GATEWAY = 5
RTA_PRIORITY = 6
RTA_PREFSRC = 7
RTA_METRICS = 8
RTA_MULTIPATH = 9
RTA_PROTOINFO = 10  # no longer used
RTA_FLOW = 11
RTA_CACHEINFO = 12
RTA_SESSION = 13  # no longer used
RTA_MP_ALGO = 14  # no longer used
RTA_TABLE = 15
RTA_MAX = 16

class RtMessage(object):
    """ A Netlink route message.
    """
    def __init__(self, family=0, dst_len=0, src_len=0, tos=0,
                       table=0, protocol=0, scope=0, type_=0,
                       flags=0, packed_data=None):
        """ Create a Netlink route message.

            Objects of this type can be used with
            pymnl.message.put_extra_header().

            family - unsigned char
            dst_len - unsigned char
            src_len - unsigned char
            tos - unsigned char

            table - unsigned char - Routing table id
            protocol - unsigned char - Routing protocol
            scope - unsigned char
            type_ - unsigned char

            flags - unsigned integer
        """
        self._format = "BBBBBBBBI"
        self._family = family
        self._dst_len = dst_len
        self._src_len = src_len
        self._tos = tos
        self._table = table
        self._protocol = protocol
        self._scope = scope
        self._type = type_
        self._flags = flags
        if (packed_data):
            packed_data = packed_data[:calcsize(self._format)]
            (self._family,
             self._dst_len,
             self._src_len,
             self._tos,
             self._table,
             self._protocol,
             self._scope,
             self._type,
             self._flags) = unpack(self._format, packed_data)

    def __len__(self):
        """
        """
        return calcsize(self._format)

    def get_binary(self):
        """ Returns a packed struct suitable for sending through a
            netlink socket.
        """
        return pack(self._format, self._family,
                                  self._dst_len,
                                  self._src_len,
                                  self._tos,
                                  self._table,
                                  self._protocol,
                                  self._scope,
                                  self._type,
                                  self._flags)

