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

'''
Share commands
'''

import json

import qumulo.lib.opts
import qumulo.lib.util
import qumulo.rest.nfs as nfs
import qumulo.rest.users as users

from qumulo.rest.nfs import NFSRestriction

def convert_nfs_user_mapping(name):
    convert = {
        'none':         'NFS_MAP_NONE',
        'root':         'NFS_MAP_ROOT',
        'all':          'NFS_MAP_ALL',
        'nfs_map_none': 'NFS_MAP_NONE',
        'nfs_map_root': 'NFS_MAP_ROOT',
        'nfs_map_all':  'NFS_MAP_ALL',
    }

    if name.lower() not in convert:
        raise ValueError('%s is not one of none, root, or all' % (name))
    return convert[name.lower()]

def process_user_mapping(user_mapping, map_to_user_id):
    user_mapping = convert_nfs_user_mapping(user_mapping)
    if user_mapping is not 'NFS_MAP_NONE' and map_to_user_id == '0':
        raise ValueError('user_mapping ' + user_mapping +
            ' requires map_to_user_id')
    if user_mapping is 'NFS_MAP_NONE' and map_to_user_id != '0':
        raise ValueError('map_to_user_id is only valid when mapping an user ' +
            '(user_mapping is not NONE). If user_mapping is NONE, remove ' +
            'map_to_user_id or make it "0".')
    return user_mapping


def parse_nfs_restrictions_file(conninfo, credentials, path):
    # Parse JSON file.
    with open(path) as f:
        contents = f.read()
        try:
            restrictions = json.loads(contents)
        except ValueError, e:
            raise ValueError('Error parsing JSON restrictions file ' + str(e))

    # Validate the restrictions are well formed, and create the
    # NFSRestriction object.
    nfs_restrictions = list()
    for r in restrictions['restrictions']:
        # Get read-only.
        read_only = r.get('read_only', False)

        # Process host restrictions.
        host_restrictions = r.get('host_restrictions', [])

        # Process user mapping values.
        try:
            user_mapping = process_user_mapping(r.get('user_mapping', 'none'),
                r.get('map_to_user_id', '0'))
        except ValueError as e:
            raise ValueError('When trying to process the following ' +
                'restriction: ' + str(r) + ', this error was thrown: ' +
                e.message)

        # Allow either auth_id or user name.
        user_id = users.get_user_id(conninfo, credentials,
            r.get('map_to_user_id', '0'))

        # Add the NFSRestriction to the list.
        nfs_restrictions.append(
            NFSRestriction({'read_only': read_only,
                            'host_restrictions': host_restrictions,
                            'user_mapping': user_mapping,
                            'map_to_user_id': str(user_id.data)}))

    # Return the list of restrictions.
    return nfs_restrictions


class NFSListSharesCommand(qumulo.lib.opts.Subcommand):
    NAME = "nfs_list_shares"
    DESCRIPTION = "List all NFS shares"

    @staticmethod
    def main(conninfo, credentials, _args):
        print nfs.nfs_list_shares(conninfo, credentials)

class NFSAddShareCommand(qumulo.lib.opts.Subcommand):
    NAME = "nfs_add_share"
    DESCRIPTION = "Add a new NFS share"

    @staticmethod
    def options(parser):
        parser.add_argument("--export-path", type=str, default=None,
            required=True, help="NFS Export path")
        parser.add_argument("--fs-path", type=str, default=None, required=True,
            help="File system path")
        parser.add_argument("--description", type=str, default='',
            help="Description of this export")
        # Require either 'no-restrictions' or the restrictions file.
        restriction_arg = parser.add_mutually_exclusive_group(required=True)
        restriction_arg.add_argument("--no-restrictions", action="store_true",
            default=False, help='Specify no restrictions for this share.')
        restriction_arg.add_argument("--restrictions", type=str, default=None,
            metavar='JSON_FILE_PATH', required=False,
            help='Path to local file containing the ' +
            'restrictions in JSON format. ' +
            'user_mapping can be "none"|"root"|"all". ' +
            'map_to_user_id may be "guest"|"admin"|"<integer_id>".   ' +
            'Example JSON: ' +
            '{ "restrictions" : [ { ' +
            '"read_only" : true, ' +
            '"host_restrictions" : [ "1.2.3.1", "1.2.3.2" ], ' +
            '"user_mapping" : "root", ' +
            '"map_to_user_id" : "guest" }, ' +
            '{<another_restriction>} ] }')
        parser.add_argument("--create-fs-path", action="store_true",
            help="Creates the specified file system path if it does not exist")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.restrictions:
            restrictions = parse_nfs_restrictions_file(conninfo, credentials,
                args.restrictions)
        else:
            restrictions = [NFSRestriction.create_default()]

        print nfs.nfs_add_share(conninfo, credentials,
            args.export_path, args.fs_path, args.description, restrictions,
            args.create_fs_path)

class NFSListShareCommand(qumulo.lib.opts.Subcommand):
    NAME = "nfs_list_share"
    DESCRIPTION = "List a share"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", type=str, default=None, required=True,
            help="ID of share to list")

    @staticmethod
    def main(conninfo, credentials, args):
        print nfs.nfs_list_share(conninfo, credentials, args.id)

class NFSModShareCommand(qumulo.lib.opts.Subcommand):
    NAME = "nfs_mod_share"
    DESCRIPTION = "Modify a share"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", type=str, default=None, required=True,
            help="ID of share to modify")
        parser.add_argument("--export-path", type=str, default=None,
            help="Change NFS export path")
        parser.add_argument("--fs-path", type=str, default=None,
            help="Change file system path")
        parser.add_argument("--description", type=str, default=None,
            help="Description of this export")
        # Do not require a restrictions argument, it will preserve the existing
        # ones.
        restriction_arg = parser.add_mutually_exclusive_group(required=False)
        restriction_arg.add_argument("--no-restrictions", action="store_true",
            default=False, help='Specify no restrictions for this share.')
        restriction_arg.add_argument("--restrictions", type=str, default=None,
            metavar='JSON_FILE_PATH', required=False,
            help='Path to local file containing the ' +
            'restrictions in JSON format. ' +
            'user_mapping can be "none"|"root"|"all". ' +
            'map_to_user_id may be "guest"|"admin"|"<integer_id>".   ' +
            'Example JSON: ' +
            '{ "restrictions" : [ { ' +
            '"read_only" : true, ' +
            '"host_restrictions" : [ "1.2.3.1", "1.2.3.2" ], ' +
            '"user_mapping" : "root", ' +
            '"map_to_user_id" : "guest" }, ' +
            '{<another_restriction>} ] }')
        parser.add_argument("--create-fs-path", action="store_true",
            help="Creates the specified file system path if it does not exist")

    @staticmethod
    def main(conninfo, credentials, args):
        # Get existing share
        share_info = {}
        share_info, share_info['if_match'] = \
            nfs.nfs_list_share(conninfo, credentials, args.id)

        # Modify share
        share_info['id_'] = share_info['id']
        share_info['allow_fs_path_create'] = args.create_fs_path
        del share_info['id']
        if args.export_path is not None:
            share_info['export_path'] = args.export_path
        if args.fs_path is not None:
            share_info['fs_path'] = args.fs_path
        if args.description is not None:
            share_info['description'] = args.description

        # Overwrite the NFS restrictions from JSON file.
        if args.restrictions:
            share_info['restrictions'] = parse_nfs_restrictions_file(
                conninfo, credentials, args.restrictions)
        elif args.no_restrictions:
            # Modify the share's restrictions to be the default ones (no
            # restrictions).
            share_info['restrictions'] = [NFSRestriction.create_default()]
        else:
            # If no restrictions were specified and the user didn't set the
            # --no-restrictions flag, let's preserve the ones that
            # were originally set for this share. However, we need to re-pack
            # them to be of type "NFSRestriction", in order to keep the REST
            # client consistent.
            share_info['restrictions'] = \
                [NFSRestriction(r) for r in share_info['restrictions']]

        print nfs.nfs_modify_share(conninfo, credentials,
            **share_info)

class NFSDeleteShareCommand(qumulo.lib.opts.Subcommand):
    NAME = "nfs_delete_share"
    DESCRIPTION = "Delete a share"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", type=str, default=None, required=True,
            help="ID of share to delete")

    @staticmethod
    def main(conninfo, credentials, args):
        nfs.nfs_delete_share(conninfo, credentials, args.id)
        print "Share has been deleted."

