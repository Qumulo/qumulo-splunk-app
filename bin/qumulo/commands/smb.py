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

'''
Share commands
'''
import qumulo.lib.opts
import qumulo.lib.util
import qumulo.rest.smb as smb
class SMBListSharesCommand(qumulo.lib.opts.Subcommand):
    NAME = "smb_list_shares"
    DESCRIPTION = "List all SMB shares"

    @staticmethod
    def main(conninfo, credentials, _args):
        print smb.smb_list_shares(conninfo, credentials)


class SMBAddShareCommand(qumulo.lib.opts.Subcommand):
    NAME = "smb_add_share"
    DESCRIPTION = "Add a new SMB share"

    @staticmethod
    def options(parser):
        parser.add_argument("--name", type=str, default=None, required=True,
            help="Name of share")
        parser.add_argument("--fs-path", type=str, default=None, required=True,
            help="File system path")
        parser.add_argument("--description", type=str, default='',
            help="Description of this share")
        parser.add_argument("--read-only", type=bool, default=False,
            help="Share cannot be used to write to the file system")
        parser.add_argument("--allow-guest-access", type=bool, default=False,
            help="Allow guest access to this share")
        parser.add_argument("--create-fs-path", action="store_true",
            help="Creates the specified file system path if it does not exist")

    @staticmethod
    def main(conninfo, credentials, args):
        print smb.smb_add_share(conninfo, credentials, args.name,
            args.fs_path, args.description, args.read_only,
            args.allow_guest_access, args.create_fs_path)

class SMBListShareCommand(qumulo.lib.opts.Subcommand):
    NAME = "smb_list_share"
    DESCRIPTION = "List a share"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", type=str, default=None, required=True,
            help="ID of share to list")

    @staticmethod
    def main(conninfo, credentials, args):
        print smb.smb_list_share(conninfo, credentials, args.id)

class SMBModShareCommand(qumulo.lib.opts.Subcommand):
    NAME = "smb_mod_share"
    DESCRIPTION = "Modify a share"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", type=str, default=None, required=True,
            help="ID of share to modify")
        parser.add_argument("--name", default=None,
            help="Change SMB share name")
        parser.add_argument("--fs-path", type=str, default=None,
            help="Change file system path")
        parser.add_argument("--description", type=str, default=None,
            help="Change description of this share")
        parser.add_argument("--read-only", type=str, default=None,
            help="Change read only")
        parser.add_argument("--allow-guest-access", type=bool, default=False,
            help="Change guest access to this share")
        parser.add_argument("--create-fs-path", action="store_true",
            help="Creates the specified file system path if it does not exist")

    @staticmethod
    def main(conninfo, credentials, args):
        share_info = {}
        share_info, share_info['if_match'] = \
            smb.smb_list_share(conninfo, credentials, args.id)

        share_info['id_'] = share_info['id']
        share_info['allow_fs_path_create'] = args.create_fs_path
        del share_info['id']
        if args.name is not None:
            share_info['share_name'] = args.name
        if args.fs_path is not None:
            share_info['fs_path'] = args.fs_path
        if args.description is not None:
            share_info['description'] = args.description
        if args.read_only is not None:
            share_info['read_only'] = \
                qumulo.lib.util.bool_from_string(args.read_only)
        if args.allow_guest_access is not None:
            share_info['allow_guest_access'] = args.allow_guest_access

        print smb.smb_modify_share(conninfo, credentials,
            **share_info)

class SMBDeleteShareCommand(qumulo.lib.opts.Subcommand):
    NAME = "smb_delete_share"
    DESCRIPTION = "Delete a share"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", type=str, default=None, required=True,
            help="ID of share to delete")

    @staticmethod
    def main(conninfo, credentials, args):
        smb.smb_delete_share(conninfo, credentials, args.id)
        print "Share has been deleted."
