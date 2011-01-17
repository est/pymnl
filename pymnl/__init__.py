# pymnl -- a minimalistic pure Python interface for netlink
# Copyright 2011 Sean Robinson <seankrobinson@gmail.com>
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

# This module is heavily influenced by the excellent libmnl
# from Pablo Neira Ayuso <pablo@netfilter.org>.  However,
# pymnl does not use libmnl.

from ctypes import *

def PYMNL_ALIGN(align_size):
    """ Return a function to calculate alignment.
    """
    return lambda len: (((len) + align_size - 1) & ~(align_size - 1))


SOCKET_BUFFER_SIZE = 8192

# define netlink-specific flags
NETLINK_ADD_MEMBERSHIP = 1
NETLINK_DROP_MEMBERSHIP = 2
NETLINK_PKTINFO = 3
NETLINK_BROADCAST_ERROR = 4
NETLINK_NO_ENOBUFS = 5

# netlink attribute types
NLA_UNSPEC = 0    # Unspecified type
NLA_U8 = 1        # 8bit integer
NLA_U16 = 2       # 16bit integer
NLA_U32 = 3       # 32bit integer
NLA_U64 = 4       # 64bit integer
NLA_STRING = 5    # character string
NLA_FLAG = 6      # flag
NLA_MSECS = 7     # micro seconds (64bit)
NLA_NESTED = 8    # nested attributes
NLA_TYPE_MAX = 9  # always keep last

NLA_F_NESTED = (1 << 15)
NLA_F_NET_BYTEORDER = (1 << 14)
NLA_TYPE_MASK = ~(NLA_F_NESTED | NLA_F_NET_BYTEORDER)




