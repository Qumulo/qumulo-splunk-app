# Copyright (c) 2013 Qumulo, Inc.
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

import qumulo.lib.opts
import qumulo.lib.util
import qumulo.rest.cluster as cluster

class ListNodesCommand(qumulo.lib.opts.Subcommand):
    NAME = "nodes_list"
    DESCRIPTION = "List nodes"

    @staticmethod
    def options(parser):
        parser.add_argument("--node", help="Node ID")

    @staticmethod
    def main(conninfo, credentials, _args):
        if _args.node is not None:
            print cluster.list_node(conninfo, credentials, _args.node)
        else:
            print cluster.list_nodes(conninfo, credentials)

class GetClusterConfCommand(qumulo.lib.opts.Subcommand):
    NAME = "cluster_conf"
    DESCRIPTION = "Get the cluster config"

    @staticmethod
    def main(conninfo, credentials, _args):
        print cluster.get_cluster_conf(conninfo, credentials)

class SetClusterConfCommand(qumulo.lib.opts.Subcommand):
    NAME = "set_cluster_conf"
    DESCRIPTION = "Set the cluster config"

    @staticmethod
    def options(parser):
        parser.add_argument("--cluster-name", help="Cluster Name",
                            required=True)

    @staticmethod
    def main(conninfo, credentials, _args):
        print cluster.put_cluster_conf(conninfo, credentials,
            _args.cluster_name)

class GetClusterSlotStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = "cluster_slots"
    DESCRIPTION = "Get the cluster disk slots status"

    @staticmethod
    def options(parser):
        parser.add_argument("--slot", help="Slot ID")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.slot is not None:
            print cluster.get_cluster_slot_status(
                conninfo, credentials, args.slot)
        else:
            print cluster.get_cluster_slots_status(
                conninfo, credentials)

class GetRestriperStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = "restriper_status"
    DESCRIPTION = "Get restriper status"

    @staticmethod
    def main(conninfo, credentials, _args):
        print cluster.get_restriper_status(conninfo, credentials)

class GetProtectionStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = "protection_status_get"
    DESCRIPTION = "Get cluster protection status"

    @staticmethod
    def main(conninfo, credentials, _args):
        print cluster.get_protection_status(conninfo, credentials)

class SetNodeIdentifyLight(qumulo.lib.opts.Subcommand):
    NAME = "set_node_identify_light"
    DESCRIPTION = "Turn node identification light on or off"

    @staticmethod
    def options(parser):
        parser.add_argument("--node", help="Node ID", required=True)
        parser.add_argument("light_state", choices=["on", "off"],
                            help="Should light be visible")

    @staticmethod
    def main(conninfo, credentials, args):
        light_visible = args.light_state == "on"
        print cluster.set_node_identify_light(conninfo, credentials,
                                              args.node, light_visible)

class GetNodeChassisStatus(qumulo.lib.opts.Subcommand):
    NAME = "node_chassis_status_get"
    DESCRIPTION = "Get the status of node chassis"

    @staticmethod
    def options(parser):
        parser.add_argument("--node", help="Node ID")

    @staticmethod
    def main(conninfo, credentials, args):
        print cluster.get_node_chassis_status(conninfo, credentials,
                                              args.node)
