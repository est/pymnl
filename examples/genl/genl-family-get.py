#!/usr/bin/python
#
# genl-family-get.py -- get info about a genl family
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
import pymnl.genl
from pymnl.attributes import Attr
from pymnl.message import Message, Payload
from pymnl.nlsocket import Socket

if (len(sys.argv) != 2):
    print("%s [family name]" % sys.argv[0])
else:
    # init and bind netlink socket
    sock = Socket(pymnl.NETLINK_GENERIC)
    sock.bind(0, 0)

    # init and build request message
    nlmsg = Message()
    nlmsg.set_type(pymnl.genl.GENL_ID_CTRL)
    nlmsg.set_flags(pymnl.message.NLM_F_REQUEST | pymnl.message.NLM_F_ACK)
    nlmsg.set_seq(randint(0, pow(2, 31)))

    # build genl header and add it to the message
    genl_header = pymnl.genl.GenlMessageHeader(
                        command=pymnl.genl.CTRL_CMD_GETFAMILY,
                        version=1)
    nlmsg.put_extra_header(genl_header)

    # init and build a payload
    payload = Payload()

    # add attributes to payload
    family_id = Attr.new_u32(pymnl.genl.CTRL_ATTR_FAMILY_ID,
                                pymnl.genl.GENL_ID_CTRL)
    payload.add_attr(family_id)
    family_name = Attr.new_strz(pymnl.genl.CTRL_ATTR_FAMILY_NAME,
                                    sys.argv[1].encode())
    payload.add_attr(family_name)
    nlmsg.add_payload(payload)

    # send message through socket
    sock.send(nlmsg)

    # read returned message from netlink
    return_msg = sock.recv(flags=socket.MSG_DONTWAIT)

    sock.close()

    # process the messages returned
    for msg in return_msg:
        if (msg.get_errno()):
            # tell the user what error occurred
            print("error:", msg.get_errstr())
        else:
            # setup and parse attributes in message payload
            genl_parser = pymnl.genl.GenlAttrParser()
            attrs = genl_parser.parse(msg.get_payload())
            print("name=%s\tid=%u\tversion=%u\thdrsize=%u\tmaxattr=%u" %
                    (attrs['name'], attrs['id'], attrs['version'],
                    attrs['hdrsize'], attrs['maxattr']))
            print("ops:")
            for op in attrs['ops'].keys():
                print("id-0x%x flags" % (op, ))
            print()
            print("grps:")
            for group in attrs['groups'].keys():
                print("id-0x%x name: %s" % (group, attrs['groups'][group]))

