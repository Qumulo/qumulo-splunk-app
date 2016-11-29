# Copyright (c) 2012 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import argparse

import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.lib.util
import qumulo.rest.network as network

class ModifyClusterNetworkConfigCommand(qumulo.lib.opts.Subcommand):
    NAME = "network_conf_mod"
    DESCRIPTION = "Modify cluster-wide network config"

    @staticmethod
    def options(parser):
        parser.add_argument("--assigned-by", choices=[ 'DHCP', 'STATIC' ],
            help="Specify mechanism for IP configuration")
        parser.add_argument("--ip-ranges", action="append",
            help="(if STATIC) IP ranges, e.g. 10.1.1.20-21")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--floating-ip-ranges", action="append",
            help="(if STATIC) Floating IP ranges, e.g. 10.1.1.20-21")
        group.add_argument("--clear-floating-ip-ranges",
            action="store_const", const=[], dest="floating_ip_ranges",
            help="(if STATIC) Remove all floating ip ranges")
        parser.add_argument("--netmask",
            help="(if STATIC) Netmask")
        parser.add_argument("--gateway",
            help="(if STATIC) Gateway address")
        parser.add_argument("--dns-servers", action="append",
            help="(if STATIC) DNS server")
        parser.add_argument("--dns-search-domains", action="append",
            help="(if STATIC) DNS search domain")
        parser.add_argument("--mtu", type=int,
             help="(if STATIC) The maximum transfer unit (MTU) in bytes")
        parser.add_argument("--bonding-mode",
             choices=[ 'ACTIVE_BACKUP', 'IEEE_8023AD' ],
             help="Ethernet bonding mode")

    @staticmethod
    def main(conninfo, credentials, args):
        if (args.assigned_by == 'DHCP'
            and any([args.dns_servers, args.dns_search_domains,
                     args.ip_ranges, args.gateway, args.netmask, args.mtu])):
            raise ValueError(
                "DHCP configuration conflicts with static configuration")

        attributes = {
            key: getattr(args, key) for key in network.V1_SETTINGS_FIELDS
                if getattr(args, key) is not None }

        if not attributes:
            raise ValueError("One or more options must be specified")

        print network.modify_cluster_network_config(conninfo, credentials,
                **attributes)

class MonitorNetworkCommand(qumulo.lib.opts.Subcommand):
    NAME = "network_poll"
    DESCRIPTION = "Poll network changes"

    @staticmethod
    def options(parser):
        parser.add_argument("--interface-id", type=int, default=1,
            help=argparse.SUPPRESS)
        parser.add_argument("--node-id", help="Node ID")
        parser.add_argument("--version", type=int, default=1,
            choices=range(1, 3), help="API version to use (default 1)")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.node_id is not None:
            if args.version == 1:
                print network.get_network_status(
                    conninfo, credentials, args.node_id)
            elif args.version == 2:
                print network.get_network_status_v2(
                    conninfo, credentials, args.interface_id, args.node_id)

        else:
            if args.version == 1:
                print network.list_network_status(conninfo, credentials)
            elif args.version == 2:
                print network.list_network_status_v2(conninfo, credentials,
                    args.interface_id)

class GetClusterNetworkConfigCommand(qumulo.lib.opts.Subcommand):
    NAME = "network_conf_get"
    DESCRIPTION = "Get cluster-wide network config"

    @staticmethod
    def main(conninfo, credentials, _args):
        print network.get_cluster_network_config(conninfo, credentials)

class GetInterfaces(qumulo.lib.opts.Subcommand):
    NAME = "network_list_interfaces"
    DESCRIPTION = argparse.SUPPRESS

    @staticmethod
    def main(conninfo, credentials, _args):
        print network.list_interfaces(conninfo, credentials)

class GetInterface(qumulo.lib.opts.Subcommand):
    NAME = "network_get_interface"
    DESCRIPTION = argparse.SUPPRESS

    @staticmethod
    def options(parser):
        parser.add_argument("--interface-id", type=int, default=1,
            help="The unique ID of the interface")

    @staticmethod
    def main(conninfo, credentials, args):
        print network.get_interface(conninfo, credentials, args.interface_id)

class GetNetworks(qumulo.lib.opts.Subcommand):
    NAME = "network_list_networks"
    DESCRIPTION = argparse.SUPPRESS

    @staticmethod
    def options(parser):
        parser.add_argument("--interface-id", type=int, default=1,
            help=argparse.SUPPRESS)

    @staticmethod
    def main(conninfo, credentials, args):
        print network.list_networks(conninfo, credentials, args.interface_id)

class GetNetwork(qumulo.lib.opts.Subcommand):
    NAME = "network_get_network"
    DESCRIPTION = argparse.SUPPRESS

    @staticmethod
    def options(parser):
        parser.add_argument("--interface-id", type=int, default=1,
            help=argparse.SUPPRESS)
        parser.add_argument("--network-id", type=int, required=True,
            help="The unique ID of the network on the interface")

    @staticmethod
    def main(conninfo, credentials, args):
        print network.get_network(conninfo, credentials,
            args.interface_id, args.network_id)

class ModInterface(qumulo.lib.opts.Subcommand):
    NAME = "network_mod_interface"
    # "Modify interface configuration"
    DESCRIPTION = argparse.SUPPRESS

    @staticmethod
    def options(parser):
        parser.add_argument("--interface-id", type=int, default=1,
            help=argparse.SUPPRESS)

        parser.add_argument("--default-gateway",
            help="The default gateway address")
        parser.add_argument("--bonding-mode",
            choices=["ACTIVE_BACKUP", "IEEE_8023AD"],
             help="Ethernet bonding mode")
        parser.add_argument("--mtu", type=int,
            help="The maximum transfer unit (MTU) in bytes")

    @staticmethod
    def main(conninfo, credentials, args):
        attributes = {
            key: getattr(args, key) for key in network.V2_INTERFACE_FIELDS
                if getattr(args, key) is not None }

        if not attributes:
            raise ValueError("One or more options must be specified")

        print network.modify_interface(conninfo, credentials, args.interface_id,
            **attributes)

class ModNetwork(qumulo.lib.opts.Subcommand):
    NAME = "network_mod_network"
    # "Modify network configuration"
    DESCRIPTION = argparse.SUPPRESS

    @staticmethod
    def options(parser):
        parser.add_argument("--interface-id", type=int, default=1,
            help=argparse.SUPPRESS)
        parser.add_argument("--network_id", type=int, required=True,
            help="The unique ID of the network on the interface")

        parser.add_argument("--assigned-by", choices=["DHCP", "STATIC"],
            help="How to assign IP address, either DHCP or STATIC")
        parser.add_argument("--ip-ranges", action="append",
            help="(if STATIC) List of IP ranges, e.g. 10.1.1.20-21")
        parser.add_argument("--floating_ip_ranges", action="append",
            help="(if STATIC) List of Floating IP ranges, e.g. 10.1.1.20-21. " \
                "Please pass in an empty string to remove floating ips.")
        parser.add_argument("--netmask",
            help="(if STATIC) IPv4 Netmask")
        parser.add_argument("--dns-servers", action="append",
            help="(if STATIC) List of DNS Servers")
        parser.add_argument("--dns-search-domains", action="append",
            help="(if STATIC) List of DNS Search Domains")
        parser.add_argument("--mtu", type=int,
            help="(if STATIC) The Maximum Transfer Unit (MTU) in bytes")
        parser.add_argument("--vlan-id", type=int,
            help="(if STATIC) User-assigned VLAN_ID for network configuration")

    @staticmethod
    def main(conninfo, credentials, args):
        attributes = {
            key: getattr(args, key) for key in network.V2_NETWORK_FIELDS
                if getattr(args, key) is not None }

        if not attributes:
            raise ValueError("One or more options must be specified")

        print network.modify_interface(conninfo, credentials, args.interface_id,
            args.network_id, **attributes)

class GetStaticIpAllocationCommand(qumulo.lib.opts.Subcommand):
    NAME = "static_ip_allocation"
    DESCRIPTION = "Get cluster-wide static IP allocation"

    @staticmethod
    def options(parser):
        parser.add_argument("--try-ranges",
            help="Specify ip range list to try "
                 "(e.g. '1.1.1.10-12,10.20.5.0/24'")
        parser.add_argument("--try-netmask",
            help="Specify netmask to apply when using --try-range option")
        parser.add_argument("--try-floating-ranges",
            help="Specify floating ip range list to try "
                 "(e.g. '1.1.1.10-12,10.20.5.0/24'")

    @staticmethod
    def main(conninfo, credentials, args):
        print network.get_static_ip_allocation(
            conninfo, credentials,
            args.try_ranges, args.try_netmask, args.try_floating_ranges)

class GetFloatingIpAllocationCommand(qumulo.lib.opts.Subcommand):
    NAME = "floating_ip_allocation"
    DESCRIPTION = "Get cluster-wide floating IP allocation"

    @staticmethod
    def main(conninfo, credentials, _args):
        print network.get_floating_ip_allocation(conninfo, credentials)
