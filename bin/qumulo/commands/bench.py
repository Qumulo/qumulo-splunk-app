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

import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.rest.bench as bench

class BenchThroughput(qumulo.lib.opts.Subcommand):
    NAME = "bench_rpc"
    DESCRIPTION = "Run an RPC benchmark test"

    @staticmethod
    def options(parser):
        parser.add_argument('--new', action='store_true',
            help='Benchmark the new RPC system')
        parser.add_argument('--target', type=int, action='store',
            default=1, help='Node id to target.')
        parser.add_argument('--blocks', type=int, action='store',
            default=1, help='Number of 4k blocks per RPC.')
        parser.add_argument('--rpcs', type=int, action='store',
            default=1, help='Number of RPCs to send.')

    @staticmethod
    def main(conninfo, credentials, args):
        if args.new:
            print bench.rpc2(
                conninfo, credentials, args.target, args.blocks, args.rpcs)
        else:
            print bench.rpc(
                conninfo, credentials, args.target, args.blocks, args.rpcs)
