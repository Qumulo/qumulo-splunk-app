# Copyright (c) 2016 Qumulo, Inc.
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
import qumulo.rest.snapshot as snapshot

class CreateSnapshotCommand(qumulo.lib.opts.Subcommand):
    NAME = "snapshot_create_snapshot"

    DESCRIPTION = "Create a new snapshot."

    @staticmethod
    def options(parser):
        parser.add_argument("-n", "--name", type=str, default=None,
            help="Name of the snapshot.")

    @staticmethod
    def main(conninfo, credentials, args):
        print snapshot.create_snapshot(conninfo, credentials, args.name)

class ListAllSnapshotsCommand(qumulo.lib.opts.Subcommand):
    NAME = "snapshot_list_snapshots"

    DESCRIPTION = "Lists all snapshots."

    @staticmethod
    def main(conninfo, credentials, _args):
        print snapshot.list_snapshots(conninfo, credentials)

class ListSnapshotCommand(qumulo.lib.opts.Subcommand):
    NAME = "snapshot_list_snapshot"

    DESCRIPTION = "Lists a single snapshot."

    @staticmethod
    def options(parser):
        parser.add_argument("-i", "--id", type=int, required=True,
            help="Identifier of the snapshot to list.")

    @staticmethod
    def main(conninfo, credentials, args):
        print snapshot.list_snapshot(conninfo, credentials, args.id)

class DeleteSnapshotCommand(qumulo.lib.opts.Subcommand):
    NAME = "snapshot_delete_snapshot"

    DESCRIPTION = "Deletes a single snapshot."

    @staticmethod
    def options(parser):
        parser.add_argument("-i", "--id", type=int, required=True,
            help="Identifier of the snapshot to delete.")

    @staticmethod
    def main(conninfo, credentials, args):
        snapshot.delete_snapshot(conninfo, credentials, args.id)
