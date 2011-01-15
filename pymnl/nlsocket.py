# nlsocket.py -- interface to netlink socket
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

import socket

class Socket:
    def __init__(self, bus):
        """ A netlink socket.

            bus - the netlink socket bus ID
                    (see NETLINK_* constants in linux/netlink.h)

            Raises an exception on error.
        """
        self._bus = bus
        self._pid = 0      # port ID
        self._groups = 0   # multicast groups mask

        self._socket = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, bus)

