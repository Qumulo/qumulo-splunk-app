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

import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.lib.util
import qumulo.rest.analytics as analytics

class GetTimeSeriesCommand(qumulo.lib.opts.Subcommand):
    NAME = "time_series_get"
    DESCRIPTION = "Get specified time series data."

    @staticmethod
    def options(parser):
        parser.add_argument("-b", "--begin-time", default=0,
            help="Begin time for time series intervals, in epoch seconds")

    @staticmethod
    def main(conninfo, credentials, args):
        print analytics.time_series_get(conninfo, credentials, args.begin_time)

class GetIopsCommand(qumulo.lib.opts.Subcommand):
    NAME = "iops_get"
    DESCRIPTION = "Get the sampled iops from the cluster. This command is " \
                  "DEPRECATED in favor of current_activity_get."

    @staticmethod
    def options(parser):
        parser.add_argument(
            '-t', '--type', type=str, default=None,
            choices=['read', 'write', 'namespace-read', 'namespace-write'],
            help="The specific type of IOPS to get")

    @staticmethod
    def main(conninfo, credentials, args):
        print analytics.iops_get(conninfo, credentials, args.type)

class GetCurrentActivityCommand(qumulo.lib.opts.Subcommand):
    NAME = "current_activity_get"
    DESCRIPTION = "Get the current sampled IOP and throughput rates"

    @staticmethod
    def options(parser):
        parser.add_argument(
            '-t', '--type', type=str, default=None,
            choices=[
                'file-iops-read',
                'file-iops-write',
                'metadata-iops-read',
                'metadata-iops-write',
                'file-throughput-read',
                'file-throughput-write'],
            help="The specific type of througput to get")

    @staticmethod
    def main(conninfo, credentials, args):
        print analytics.current_activity_get(conninfo, credentials, args.type)

class GetCapacityHistoryCommand(qumulo.lib.opts.Subcommand):
    NAME = "capacity_history_get"
    DESCRIPTION = "Get capacity history data."

    @staticmethod
    def options(parser):
        parser.add_argument(
            '--begin-time', type=int, required=True,
            help='Lower bound on history returned, in epoch seconds.')
        parser.add_argument(
            '--end-time', type=int, required=False,
            help='Upper bound on history returned, in epoch seconds. '\
                 'Defaults to the most recent period for which data is '\
                 'available.')
        parser.add_argument(
            '--interval', type=str, default='hourly',
            choices=['hourly', 'daily', 'weekly'],
            help='The interval at which to sample')

    @staticmethod
    def main(conninfo, credentials, args):
        print analytics.capacity_history_get(conninfo, credentials,
            args.interval, args.begin_time, args.end_time)

class GetCapacityHistoryFilesCommand(qumulo.lib.opts.Subcommand):
    NAME = "capacity_history_files_get"
    DESCRIPTION = "Get historical largest file data."

    @staticmethod
    def options(parser):
        parser.add_argument(
            '--timestamp', type=int, required=True,
            help='Time period to retrieve, in epoch seconds.')

    @staticmethod
    def main(conninfo, credentials, args):
        print analytics.capacity_history_files_get(conninfo, credentials,
            args.timestamp)



