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

def PYMNL_ALIGN(align_size):
    """ Return a function to calculate alignment.
    """
    return lambda len: (((len) + align_size - 1) & ~(align_size - 1))

#
# linux/netlink.h
#

# netlink types
NETLINK_ROUTE = 0             # Routing/device hook
NETLINK_UNUSED = 1            # Unused number
NETLINK_USERSOCK = 2          # Reserved for user mode socket protocols
NETLINK_FIREWALL = 3          # Firewalling hook
NETLINK_INET_DIAG = 4         # INET socket monitoring
NETLINK_NFLOG = 5             # netfilter/iptables ULOG
NETLINK_XFRM = 6              # ipsec
NETLINK_SELINUX = 7           # SELinux event notifications
NETLINK_ISCSI = 8             # Open-iSCSI
NETLINK_AUDIT = 9             # auditing
NETLINK_FIB_LOOKUP = 10
NETLINK_CONNECTOR = 11
NETLINK_NETFILTER = 12        # netfilter subsystem
NETLINK_IP6_FW = 13
NETLINK_DNRTMSG = 14          # DECnet routing messages
NETLINK_KOBJECT_UEVENT = 15   # Kernel messages to userspace
NETLINK_GENERIC = 16
NETLINK_SCSITRANSPORT = 18    # SCSI Transports
NETLINK_ECRYPTFS = 19

MAX_LINKS = 32

NETLINK_ADD_MEMBERSHIP = 1
NETLINK_DROP_MEMBERSHIP = 2
NETLINK_PKTINFO = 3
NETLINK_BROADCAST_ERROR = 4
NETLINK_NO_ENOBUFS = 5

NET_MAJOR = 36          # Major 36 is reserved for networking

