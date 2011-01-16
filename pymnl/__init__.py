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

SOCKET_BUFFER_SIZE = 8192

# define netlink-specific flags
NETLINK_ADD_MEMBERSHIP = 1
NETLINK_DROP_MEMBERSHIP = 2
NETLINK_PKTINFO = 3
NETLINK_BROADCAST_ERROR = 4
NETLINK_NO_ENOBUFS = 5

_ALIGNTO = 4
def align(len):
    """ Align to _ALIGNTO boundary.

        Copied from libmnl.h.
    """
    return (((len) + _ALIGNTO - 1) & ~(_ALIGNTO - 1))


