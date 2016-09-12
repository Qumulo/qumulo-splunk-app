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

import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.rest.fs as fs
import qumulo.lib.request as request

import qumulo.lib.util

import os.path
import sys
import json

AGG_ORDERING_CHOICES = [
    "total_blocks",
    "total_datablocks",
    "total_metablocks",
    "total_files",
    "total_directories",
    "total_symlinks",
    "total_other",
    "max_ctime"]

LOCK_RELEASE_FORCE_MSG = "Manually releasing locks may cause data corruption, "\
                         "do you want to proceed?"

def all_elements_none(iterable):
    for element in iterable:
        if element is not None:
            return False
    return True

class GetStatsCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_get_stats"
    DESCRIPTION = "Get file system statistics"

    @staticmethod
    def main(conninfo, credentials, _args):
        print fs.read_fs_stats(conninfo, credentials)

class GetFileAttrCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_file_get_attr"
    DESCRIPTION = "Get file attributes"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", help="File ID", type=str, required=True)
        parser.add_argument("--snapshot", help="Snapshot ID to read from",
            type=int)

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.get_file_attr(conninfo, credentials, args.id,
            snapshot=args.snapshot)

class SetFileAttrCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_file_set_attr"
    DESCRIPTION = "Set file attributes"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", help="File id", type=str, required=True)
        parser.add_argument("--mode", type=str,
                            help="Posix-style file mode (octal)")
        parser.add_argument("--owner", help="File owner", type=str)
        parser.add_argument("--group", help="File group", type=str)
        parser.add_argument("--size", help="File size", type=str)
        parser.add_argument("--creation-time", type=str,
                            help='File creation time (as RFC 3339 string)')
        parser.add_argument("--modification-time", type=str,
                            help='File modification time (as RFC 3339 string)')
        parser.add_argument("--change-time", type=str,
                            help='File change time (as RFC 3339 string)')

    @staticmethod
    def main(conninfo, credentials, args):
        if all_elements_none([args.mode, args.owner, args.group, args.size,
                              args.creation_time, args.modification_time,
                              args.change_time]):
            raise ValueError("Must specify at least one option to change.")

        print fs.set_file_attr(conninfo, credentials,
                args.mode, args.owner, args.group, args.size,
                args.creation_time, args.modification_time, args.change_time,
                args.id)

class GetAclCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_get_acl"
    DESCRIPTION = "Get file ACL"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", help="Path to file", type=str)
        parser.add_argument("--id", help="File ID", type=str)
        parser.add_argument("--snapshot", help="Snapshot ID to read from",
            type=int)

    @staticmethod
    def main(conninfo, credentials, args):
        if args.id and args.path:
            raise ValueError("--path conflicts with --id")
        elif not args.id and not args.path:
            raise ValueError("Must specify --path or --id")

        print fs.get_acl(conninfo, credentials, args.path, args.id,
            snapshot=args.snapshot)

class SetAclCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_set_acl"
    DESCRIPTION = "Set file ACL"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", help="Path to file", type=str)
        parser.add_argument("--id", help="File id", type=str)
        parser.add_argument("--file", help="Local file containing ACL JSON"
                            " containing control flags and ACEs",
                            required=False, type=str)

    @staticmethod
    def main(conninfo, credentials, args):
        if args.id and args.path:
            raise ValueError("--path conflicts with --id")
        elif not args.id and not args.path:
            raise ValueError("Must specify --path or --id")
        if not bool(args.file):
            raise ValueError('Must specify --file')

        acl_control = None
        acl_aces = None
        with open(args.file) as f:
            contents = f.read()
            try:
                acl_contents = json.loads(contents)
                acl = acl_contents.get("acl")
                acl_control = acl.get("control")
                acl_aces = acl.get("aces")
            except ValueError, e:
                raise ValueError("Error parsing ACL data: %s\n" % str(e))

        etag = None
        print fs.set_acl(conninfo, credentials, path=args.path,
                id_=args.id, control=acl_control, aces=acl_aces,
                if_match=etag)

class CreateFileCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_create_file"
    DESCRIPTION = "Create a new file"

    @staticmethod
    def options(parser):
        parser.add_argument("--name", help="New file name", required=True)
        parser.add_argument("--path", help="Path to parent directory")
        parser.add_argument("--id", help="ID of parent directory")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.id and args.path:
            raise ValueError("--path conflicts with --id")
        elif not args.id and not args.path:
            raise ValueError("Must specify --path or --id")

        print fs.create_file(conninfo, credentials, args.name,
            dir_path=args.path, dir_id=args.id)

class CreateDirectoryCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_create_dir"
    DESCRIPTION = "Create a new directory"

    @staticmethod
    def options(parser):
        parser.add_argument("--name", help="New directory name", required=True)
        parser.add_argument("--path", help="Path to parent directory")
        parser.add_argument("--id", help="ID of parent directory")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.id and args.path:
            raise ValueError("--path conflicts with --id")
        elif not args.id and not args.path:
            raise ValueError("Must specify --path or --id")

        print fs.create_directory(conninfo, credentials, args.name,
            dir_path=args.path, dir_id=args.id)

class CreateSymlinkCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_create_symlink"
    DESCRIPTION = "Create a new symbolic link"

    @staticmethod
    def options(parser):
        parser.add_argument("--name", help="New symlink name", required=True)
        parser.add_argument("--path", help="Path to parent directory")
        parser.add_argument("--id", help="ID of parent directory")
        parser.add_argument("--target", help="Link target", required=True)
        parser.add_argument("--target-type", help="Link target type")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.id and args.path:
            raise ValueError("--path conflicts with --id")
        elif not args.id and not args.path:
            raise ValueError("Must specify --path or --id")

        print fs.create_symlink(
            conninfo,
            credentials,
            args.name,
            args.target,
            dir_path=args.path,
            dir_id=args.id,
            target_type=args.target_type)

class CreateLinkCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_create_link"
    DESCRIPTION = "Create a new link"

    @staticmethod
    def options(parser):
        parser.add_argument("--name", help="New link name", required=True)
        parser.add_argument("--path", help="Path to parent directory")
        parser.add_argument("--id", help="ID of parent directory")
        parser.add_argument("--target", help="Link target", required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        if args.id and args.path:
            raise ValueError("--path conflicts with --id")
        elif not args.id and not args.path:
            raise ValueError("Must specify --path or --id")

        print fs.create_link(conninfo, credentials, args.name,
            args.target, dir_path=args.path, dir_id=args.id)

class RenameCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_rename"
    DESCRIPTION = "Rename a file system object"

    @staticmethod
    def options(parser):
        parser.add_argument("--name", help="New name", required=True)
        parser.add_argument("--path", help="Path to parent directory")
        parser.add_argument("--id", help="ID of parent directory")
        parser.add_argument("--source", help="Source file path", required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        if args.id and args.path:
            raise ValueError("--path conflicts with --id")
        elif not args.id and not args.path:
            raise ValueError("Must specify --path or --id")

        print fs.rename(conninfo, credentials, args.name,
            args.source, dir_path=args.path, dir_id=args.id)

class DeleteCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_delete"
    DESCRIPTION = "Delete a file system object"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", help="Path to file", required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        fs.delete(conninfo, credentials, args.path)
        print "File system object was deleted."

class WriteFileCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_write"
    DESCRIPTION = "Write a file"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", help="Path to file", type=str)
        parser.add_argument("--id", help="File id", type=str)
        parser.add_argument("--file", help="File data to send", type=str)
        parser.add_argument("--create", action="store_true",
                            help="Create file before writing (fails if exists)")
        parser.add_argument("--stdin", action="store_true",
                            help="Write file from stdin")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.id and args.create:
            raise ValueError("cannot use --create with --id")
        if args.id and args.path:
            raise ValueError("--path conflicts with --id")
        elif not args.id and not args.path:
            raise ValueError("Must specify --path or --id")
        if args.stdin:
            if args.file:
                raise ValueError("--stdin conflicts with --file")
            elif not args.chunked:
                raise ValueError("--stdin must be sent chunked")
        elif args.file:
            if not os.path.isfile(args.file):
                raise ValueError("%s is not a file" % args.file)
        else:
            raise ValueError("Must specify --stdin or --file")

        infile = open(args.file, "rb") if args.file else sys.stdin

        if args.create:
            dirname, basename = qumulo.lib.util.unix_path_split(args.path)
            if not basename:
                raise ValueError("Path has no basename")
            fs.create_file(conninfo, credentials, basename, dirname)

        etag = None
        print fs.write_file(conninfo, credentials, infile,
            args.path, args.id, etag)

class ReadFileCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_read"
    DESCRIPTION = "Read a file"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", help="Path to file", type=str)
        parser.add_argument("--id", help="File id", type=str)
        parser.add_argument("--snapshot", help="Snapshot ID to read from",
                            type=int)
        parser.add_argument("--file", help="File to receive data", type=str)
        parser.add_argument("--force", action='store_true',
                            help="Overwrite an existing file")
        parser.add_argument("--stdout", action='store_const', const=True,
                            help="Output data to standard out")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.stdout:
            if args.file:
                raise ValueError("--stdout conflicts with --file")
        elif args.file:
            if os.path.exists(args.file) and not args.force:
                raise ValueError("%s already exists." % args.file)
        else:
            raise ValueError("Must specify --stdout or --file")

        if args.id and args.path:
            raise ValueError("--path conflicts with --id")
        elif not args.id and not args.path:
            raise ValueError("Must specify --path or --id")

        if args.file is None:
            f = sys.stdout
        else:
            f = open(args.file, "wb")

        fs.read_file(conninfo, credentials, f, path=args.path,
            id_=args.id, snapshot=args.snapshot)
        # Print nothing on success (File may be output into stdout)

class ReadDirectoryCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_read_dir"
    DESCRIPTION = "Read directory"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", help="Directory path", type=str)
        parser.add_argument("--id", help="Directory id", type=str)
        parser.add_argument("--page-size", type=int,
                            help="Max directory entries to return per request")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.id and args.path:
            raise ValueError("--path conflicts with --id")
        elif not args.id and not args.path:
            raise ValueError("Must specify --path or --id")
        elif args.page_size is not None and args.page_size < 1:
            raise ValueError("Page size must be greater than 0")

        page = fs.read_directory(conninfo, credentials, args.page_size,
                                        args.path, args.id)
        print page
        next_uri = json.loads(str(page))["paging"]["next"]
        while next_uri != "":
            page = request.rest_request(conninfo, credentials, "GET", next_uri)
            print page
            next_uri = json.loads(str(page))["paging"]["next"]

class ReadDirectoryCapacityCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_read_dir_aggregates"
    DESCRIPTION = "Read directory aggregation entries"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", help="Directory path", type=str,
            required=True)
        parser.add_argument("--recursive", action="store_true",
            help="Fetch recursive aggregates")
        parser.add_argument("--max-entries",
            help="Maximum number of entries to return", type=int)
        parser.add_argument("--max-depth",
            help="Maximum depth to recurse when --recursive is set", type=int)
        parser.add_argument("--order-by", choices=AGG_ORDERING_CHOICES,
            help="Specify field used for top N selection and sorting")

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.read_dir_aggregates(conninfo, credentials, args.path,
                args.recursive, args.max_entries, args.max_depth, args.order_by)

class TreeWalkCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_walk_tree"
    DESCRIPTION = "Walk file system tree"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", help="Path to tree root", type=str,
                            required=False, default='/')

    @staticmethod
    def main(conninfo, credentials, args):
        for f, _etag in fs.tree_walk_preorder(conninfo, credentials, args.path):
            print '%s sz=%s owner=%s group=%s ' \
                  'owner_id_type=%s owner_id_value=%s ' \
                  'group_id_type=%s group_id_value=%s' % (
                f['path'], f['size'], f['owner'],
                f['group'], f['owner_details']['id_type'],
                str(f['owner_details']['id_value']),
                f['group_details']['id_type'],
                str(f['group_details']['id_value']))

class TreeDeleteCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_delete_tree"
    DESCRIPTION = "Walk file system tree and delete"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", help="Path to tree root", type=str,
                            required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        for f, _etag in fs.tree_walk_postorder(
                conninfo, credentials, args.path):
            fs.delete(conninfo, credentials, f['path'])
        print "Tree delete was successful."

class GetFileSamplesCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_file_samples"
    DESCRIPTION = "Get a number of sample files from the file system"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", required=True)
        parser.add_argument("--count", type=int, required=True)
        parser.add_argument("--sample-by",
                            choices=['capacity', 'input-ops', 'file'],
                            help="Weight sampling by the given value")

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.get_file_samples(conninfo, credentials, args.path, args.count,
                                  args.sample_by)

class ResolvePathsCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_resolve_paths"
    DESCRIPTION = "Resolve file IDs to paths"

    @staticmethod
    def options(parser):
        parser.add_argument("--ids", required=True, nargs="*",
            help="File IDs to resolve")

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.resolve_paths(conninfo, credentials, args.ids)

class ListLocksByFileCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_list_locks_by_file"
    DESCRIPTION = "List locks held on a particular files"

    @staticmethod
    def options(parser):
        parser.add_argument("--protocol", type=str, required=True,
            choices = { p for p, t in fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS },
            help="The protocol whose locks should be listed")
        parser.add_argument("--lock-type", type=str, required=True,
            choices = { t for p, t in fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS },
            help="The type of lock to list.")
        parser.add_argument("--path", help="File path", type=str)
        parser.add_argument("--id", help="File id", type=str)

    @staticmethod
    def main(conninfo, credentials, args):
        if args.id and args.path:
            raise ValueError("--path conflicts with --id")
        elif not args.id and not args.path:
            raise ValueError("Must specify --path or --id")

        if (args.protocol, args.lock_type) not in \
                fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS:
            raise ValueError(
                "Lock type {} not available for protocol {}".format(
                    args.lock_type, args.protocol))

        print json.dumps(
            fs.list_all_locks_by_file(
                conninfo,
                credentials,
                args.protocol,
                args.lock_type,
                args.path,
                args.id),
            indent=4)

class ListLocksByClientCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_list_locks_by_client"
    DESCRIPTION = "List locks held by a particular client machine"

    @staticmethod
    def options(parser):
        parser.add_argument("--protocol", type=str, required=True,
            choices = { p for p, t in fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS },
            help="The protocol whose locks should be listed")
        parser.add_argument("--lock-type", type=str, required=True,
            choices = { t for p, t in fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS },
            help="The type of lock to list.")
        parser.add_argument("--name", help="Client hostname", type=str)
        parser.add_argument("--address", help="Client IP address", type=str)

    @staticmethod
    def main(conninfo, credentials, args):
        if (args.protocol, args.lock_type) not in \
                fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS:
            raise ValueError(
                "Lock type {} not available for protocol {}".format(
                    args.lock_type, args.protocol))

        if args.name and (args.protocol != 'nlm'):
            raise ValueError("--name may only be specified for NLM locks")

        print json.dumps(
            fs.list_all_locks_by_client(
                conninfo,
                credentials,
                args.protocol,
                args.lock_type,
                args.name,
                args.address),
            indent=4)

class ReleaseNLMLocksByClientCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_release_nlm_locks_by_client"
    DESCRIPTION = '''Release NLM byte range locks held by client. This method
    releases all locks held by a particular client. This is dangerous, and
    should only be used after confirming that the client is dead.'''

    @staticmethod
    def options(parser):
        parser.add_argument("--force",
            help="This command can cause corruption, add this flag to \
                release lock", action='store_true', required=False)
        parser.add_argument("--name", help="Client hostname", type=str)
        parser.add_argument("--address", help="Client IP address", type=str)

    @staticmethod
    def main(conninfo, credentials, args):
        if not args.name and not args.address:
            raise ValueError("Must specify --name or --address")

        if not args.force and not qumulo.lib.opts.ask(
                ReleaseNLMLocksByClientCommand.NAME, LOCK_RELEASE_FORCE_MSG):
            return # Operation cancelled.

        fs.release_nlm_locks_by_client(
                conninfo,
                credentials,
                args.name,
                args.address)
        params = ""
        if args.name:
            params += "owner_name: {}".format(args.name)
        if args.name and args.address:
            params += ", "
        if args.address:
            params += "owner_address: {}".format(args.address)
        print "NLM byte-range locks held by {} were released.".format(params)

class ReleaseNLMLockCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_release_nlm_lock"
    DESCRIPTION = '''Release an arbitrary NLM byte-range lock range. This is
    dangerous, and should only be used after confirming that the owning process
    has leaked the lock, and only if there is a very good reason why the
    situation should not be resolved by terminating that process.'''

    @staticmethod
    def options(parser):
        parser.add_argument("--offset", help="NLM byte-range lock offset",
                required=True, type=str)
        parser.add_argument("--size", help="NLM byte-range lock size",
                required=True, type=str)
        parser.add_argument("--owner-id", help="Owner id",
                required=True, type=str)
        parser.add_argument("--force",
                help="This command can cause corruption, add this flag to \
                        release lock", action='store_true', required=False)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="File path", type=str)
        group.add_argument("--id", help="File id", type=str)

    @staticmethod
    def main(conninfo, credentials, args):
        if not args.force and not qumulo.lib.opts.ask(
                ReleaseNLMLockCommand.NAME, LOCK_RELEASE_FORCE_MSG):
            return # Operation cancelled.

        fs.release_nlm_lock(
                conninfo,
                credentials,
                args.offset,
                args.size,
                args.owner_id,
                args.path,
                args.id)
        output = ("NLM byte-range lock with "
                    "(offset: {0}, "
                    "size: {1}, "
                    "owner-id: {2}, "
                    "{3}) "
                    "was released.")
        print output.format(args.offset,
                args.size,
                args.owner_id,
                "file_path: {}".format(args.path) if args.path is not None \
                else "file_id: {}".format(args.id))
