#!/usr/bin/python
#
# rtnl-route-dump.py -- dump kernel routing info from rtnetlink
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
import struct
import sys

import pymnl
from pymnl.attributes import Attr, AttrParser
from pymnl.message import Message, Payload
from pymnl.nlsocket import Socket

import if_
import if_link
import rtnetlink

class RouteParser(AttrParser):
    """ Parser for routing info.
    """
    def __init__(self):
        # dict to hold attributes without an assigned callback
        self._attributes = { 'unmatched': [] }

        self._cb = {rtnetlink.RTA_TABLE : self.rta_table,
                    rtnetlink.RTA_DST : self.rta_dst,
                    rtnetlink.RTA_SRC : self.rta_src,
                    rtnetlink.RTA_OIF : self.rta_oif,
                    rtnetlink.RTA_FLOW : self.rta_flow,
                    rtnetlink.RTA_PREFSRC : self.rta_prefsrc,
                    rtnetlink.RTA_GATEWAY : self.rta_gateway,
                    rtnetlink.RTA_METRICS : self.rta_metrics}

    def rta_table(self, attr):
        self._attributes['table'] = attr.get_u32()

    def rta_dst(self, attr):
        dst = struct.pack("L", attr.get_u32())
        self._attributes['dst'] = socket.inet_ntoa(dst)

    def rta_src(self, attr):
        src = struct.pack("L", attr.get_u32())
        self._attributes['src'] = socket.inet_ntoa(src)

    def rta_oif(self, attr):
        self._attributes['oif'] = attr.get_u32()

    def rta_flow(self, attr):
        self._attributes['flow'] = attr.get_u32()

    def rta_prefsrc(self, attr):
        prefsrc = struct.pack("L", attr.get_u32())
        self._attributes['prefsrc'] = socket.inet_ntoa(prefsrc)

    def rta_gateway(self, attr):
        gateway = struct.pack("L", attr.get_u32())
        self._attributes['gw'] = socket.inet_ntoa(gateway)

    def rta_metrics(self, attr):
        """ Parse nested attributes.

            attr - Attr object
        """
        self._attributes['metrics'] = {}
        # process a list of nested attributes
        for one_attr in RouteMetricsParser().parse_nested(attr):
            # get list of nested nested attributes  <-- not a typo
            nested_attrs = RouteMetricsParser().parse_nested(one_attr)
            # save nested attributes to 'ops' dictionary
            self._attributes['metrics'][nested_attrs[0].get_u32()] = \
                                                nested_attrs[1].get_u32()

    def parse(self, data, offset=0):
        """ Process the attributes.

            data - object with attributes
        """
        for one_attr in self.parse_string(data.get_binary(), offset):
            try:
                self._cb[one_attr.get_type()](one_attr)
            except KeyError:
                self._attributes['unmatched'].append(one_attr)

        return self._attributes


class RouteMetricsParser(AttrParser):
    """ Parser for route metrics.
    """
    def __init__(self):
        # list to hold attributes without an assigned callback
        self._attributes = []

        self._cb = {RTAX_MAX : self.rtax_max}

    def rtax_max(self, attr):
        self._attributes.append(attr.get_u32())



# init and build request message
rtnlmsg = Message()
rtnlmsg.set_type(rtnetlink.RTM_GETROUTE)
rtnlmsg.set_flags(pymnl.message.NLM_F_REQUEST | pymnl.message.NLM_F_DUMP)

sequence = randint(0, pow(2, 31))
rtnlmsg.set_seq(sequence)

# build rtgenmsg header and add it to the message
rtmsg_header = rtnetlink.RtGenMessageHeader()
rtmsg_header._family = socket.AF_INET
rtnlmsg.put_extra_header(rtmsg_header)

# init and bind netlink socket
sock = Socket(pymnl.NETLINK_ROUTE)
sock.bind(pymnl.nlsocket.SOCKET_AUTOPID, 0)

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
        rtm = rtnetlink.RtMessage(packed_data=msg.get_payload())
        line = ""
        # protocol family = AF_INET | AF_INET6
        line = line + ("family=%u " % (rtm._family,))
        # destination CIDR, eg. 24 or 32 for IPv4
        line = line + ("dst_len=%u " % (rtm._dst_len,))
        # source CIDR
        line = line + ("src_len=%u " % (rtm._src_len,))
        # type of service (TOS), eg. 0
        line = line + ("tos=%u " % (rtm._tos,))
        # table id
        line = line + ("table=%u " % (rtm._table,))
        # type
        line = line + ("type=%u " % (rtm._type,))
        # scope
        line = line + ("scope=%u " % (rtm._scope,))
        # protocol
        line = line + ("proto=%u " % (rtm._protocol,))
        # flags
        line = line + ("flags=%x" % (rtm._flags,))
        print(line)

        route_parser = RouteParser()
        attrs = route_parser.parse(msg.get_payload(), len(rtm))
        line = ""
        try:
            line = line + ("table=%u " % (attrs['table'],))
        except KeyError:
            pass
        try:
            line = line + ("dst=%s " % (attrs['dst'],))
        except KeyError:
            pass
        try:
            line = line + ("src=%s " % (attrs['src'],))
        except KeyError:
            pass
        try:
            line = line + ("oif=%u " % (attrs['oif'],))
        except KeyError:
            pass
        try:
            line = line + ("flow=%u " % (attrs['flow'],))
        except KeyError:
            pass
        try:
            line = line + ("prefsrc=%s " % (attrs['prefsrc'],))
        except KeyError:
            pass
        try:
            line = line + ("gw=%s " % (attrs['gateway'],))
        except KeyError:
            pass
        print(line)

