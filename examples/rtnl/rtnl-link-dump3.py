#!/usr/bin/python
#
# rtnl-link-dump3.py -- dump kernel routing info from rtnetlink
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

# init and bind netlink socket
sock = Socket(pymnl.NETLINK_ROUTE)
sock.bind(pymnl.nlsocket.SOCKET_AUTOPID, 0)

# init and build request message
rtnlmsg = Message()
rtnlmsg.set_type(rtnetlink.RTM_GETLINK)
rtnlmsg.set_flags(pymnl.message.NLM_F_REQUEST | pymnl.message.NLM_F_DUMP)

sequence = randint(0, pow(2, 31))
rtnlmsg.set_seq(sequence)

# build rtgenmsg header and add it to the message
rtgenmsg_header = rtnetlink.RtGenMessageHeader(socket.AF_PACKET)
rtnlmsg.put_extra_header(rtgenmsg_header)

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
    else:
        # use the payload data to create interface info message
        ifm = if_.IfInfoMessage(msg.get_payload().get_binary())
        # begin output line with interface info
        line = ("index=%d type=%d flags=%d family=%d " %
                (ifm.index, ifm.type_, ifm.flags, ifm.family))

        # add running status to output line
        if (ifm.flags & if_.IFF_RUNNING):
            line = line + "[RUNNING] "
        else:
            line = line + "[NOT RUNNING] "

        ifla_parser = if_link.IFLAttrParser()
        # make a payload with the interface link attributes data
        ifla_payload = Payload(msg.get_payload().get_binary()[len(ifm):])
        # parse the new payload into a dict of Attrs
        attrs = ifla_parser.parse(ifla_payload)

        # add final interface info to output line
        line = line + ("name=%s mtu=%d " % (attrs['ifname'], attrs['mtu']))

        # finally output the dang line
        print(line)

