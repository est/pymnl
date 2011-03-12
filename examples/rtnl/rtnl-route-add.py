#!/usr/bin/python
#
# rtnl-link-add.py -- add a route
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

import ctypes
from random import randint
import socket
from struct import pack, unpack
import sys

import pymnl
from pymnl.attributes import Attr
from pymnl.message import Message, Payload
from pymnl.nlsocket import Socket

import if_
import if_link
import rtnetlink

if (len(sys.argv) <= 3):
    print("Usage: %s iface destination cidr [gateway]" % sys.argv[0]);
    print("Example: %s eth0 10.0.1.12 32 10.0.1.11" % sys.argv[0]);
    sys.exit()

libc = ctypes.CDLL("libc.so.6")

iface = libc.if_nametoindex(sys.argv[1].encode())
if (iface == 0):
    print("Bad interface name")
    sys.exit()

try:
    dst = unpack("L", socket.inet_pton(socket.AF_INET, sys.argv[2]))[0]
except socket.error:
    print("Bad destination")
    sys.exit()

try:
    mask = int(sys.argv[3])
except:
    print("Bad CIDR")
    sys.exit()

if (len(sys.argv) >= 5):
    try:
        gw = unpack("L", socket.inet_pton(socket.AF_INET, sys.argv[4]))[0]
    except:
        print("Bad gateway")
        sys.exit()

# init and build request message
rtnlmsg = Message()
rtnlmsg.set_type(rtnetlink.RTM_NEWROUTE)
rtnlmsg.set_flags(pymnl.message.NLM_F_REQUEST | pymnl.message.NLM_F_CREATE)
rtnlmsg.set_seq(randint(0, pow(2, 31)))

# build ifm header and add it to the message
rtm = rtnetlink.RtMessage()
rtm._family = socket.AF_INET
rtm._dst_len = mask
rtm._src_len = 0
rtm._tos = 0
rtm._protocol = rtnetlink.RTPROT_BOOT
rtm._table = rtnetlink.RT_TABLE_MAIN
rtm._type = rtnetlink.RTN_UNICAST
# Is there any gateway?
if (len(sys.argv) == 4):
    rtm._scope = rtnetlink.RT_SCOPE_LINK
else:
    rtm._scope = rtnetlink.RT_SCOPE_UNIVERSE
rtm._flags = 0

rtnlmsg.put_extra_header(rtm)

payload = rtnlmsg.get_payload()
payload.add_attr(Attr.new_u32(rtnetlink.RTA_DST, dst))
payload.add_attr(Attr.new_u32(rtnetlink.RTA_OIF, iface))
if (len(sys.argv) >= 5):
    payload.add_attr(Attr.new_u32(rtnetlink.RTA_GATEWAY, gw))

# init and bind netlink socket
sock = Socket(pymnl.NETLINK_ROUTE)
sock.bind(pymnl.nlsocket.SOCKET_AUTOPID, 0)

# send message through socket
sock.send(rtnlmsg)

# ignore any return messages

sock.close()

