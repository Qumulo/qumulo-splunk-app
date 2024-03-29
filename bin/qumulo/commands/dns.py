# Copyright (c) 2015 Qumulo, Inc.
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
import qumulo.rest.dns as dns

import qumulo.lib.util

class ResolveIpAddresses(qumulo.lib.opts.Subcommand):
    NAME = "dns_resolve_ips"
    DESCRIPTION = "Resolve IP addresses to hostnames"

    @staticmethod
    def options(parser):
        parser.add_argument("--ips", required=True, nargs="*",
            help="IP addresses to resolve")

    @staticmethod
    def main(conninfo, credentials, args):
        print dns.resolve(conninfo, credentials, args.ips)
