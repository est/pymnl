#!/usr/bin/python
#
# rtnl-link-set.py -- set an interface up or down
# Copyright 2011 Sean Robinson <seankrobinson@gmail.com>
#
# This file is part of the pymnl package, a Python interface
# for netlink sockets.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

from __future__ import print_function

from random import randint
import socket
import sys

import pymnl
from pymnl.attributes import Attr
from pymnl.message import Message, Payload
from pymnl.nlsocket import Socket

import if_
import if_link
import rtnetlink

change = 0
flags = 0

if (len(sys.argv) != 3):
    print("Usage: %s [ifname] [up|down]" % (sys.argv[0],))
    sys.exit()

if (sys.argv[2].lower() == "up"):
    change |= if_.IFF_UP
    flags |= if_.IFF_UP
elif (sys.argv[2].lower() == "down"):
    change |= if_.IFF_UP;
    flags &= ~if_.IFF_UP;
else:
    print("%s is not `up' nor `down'" % (sys.argv[2],))
    sys.exit()

# init and build request message
rtnlmsg = Message()
rtnlmsg.set_type(rtnetlink.RTM_NEWLINK)
rtnlmsg.set_flags(pymnl.message.NLM_F_REQUEST | pymnl.message.NLM_F_ACK)

sequence = randint(0, pow(2, 31))
rtnlmsg.set_seq(sequence)

# build ifm header and add it to the message
ifm = if_.IfInfoMessage()
ifm.family = socket.AF_UNSPEC
ifm.change = change
ifm.flags = flags

rtnlmsg.put_extra_header(ifm)

payload = rtnlmsg.get_payload()
payload.add_attr(Attr.new_strnz(if_link.IFLA_IFNAME, sys.argv[1].encode()))

# init and bind netlink socket
sock = Socket(pymnl.NETLINK_ROUTE)
sock.bind(pymnl.nlsocket.SOCKET_AUTOPID, 0)

rtnlmsg.printf(len(ifm))

# send message through socket
sock.send(rtnlmsg)

# read returned message from netlink
return_msg = sock.recv(flags=socket.MSG_DONTWAIT)

sock.close()

# process the messages returned
for msg in return_msg:
    if (msg.get_errno()):
        # tell the user what error occurred
        print("error:", msg.get_errstr())


