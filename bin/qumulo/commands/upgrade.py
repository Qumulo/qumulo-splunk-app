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

import argparse

import qumulo.lib.opts
import qumulo.lib.util
import qumulo.rest.upgrade as upgrade

import time

def convert_target(target):
    convert = {
        'idle':                   'UPGRADE_TARGET_IDLE',
        'prepare':                'UPGRADE_TARGET_PREPARE',
        'arm':                    'UPGRADE_TARGET_ARM',
        'upgrade_target_idle':    'UPGRADE_TARGET_IDLE',
        'upgrade_target_prepare': 'UPGRADE_TARGET_PREPARE',
        'upgrade_target_arm':     'UPGRADE_TARGET_ARM',
    }

    if target.lower() not in convert:
        raise ValueError('%s not one of idle, prepare, or arm' % (target))
    return convert[target.lower()]

class UpgradeConfigCommand(qumulo.lib.opts.Subcommand):
    NAME = "upgrade_config"
    DESCRIPTION = "List current upgrade prepare config"

    @staticmethod
    def main(conninfo, credentials, _args):
        print upgrade.config_get(conninfo, credentials)

class UpgradePrepareCommand(qumulo.lib.opts.Subcommand):
    NAME = "upgrade_config_set"
    DESCRIPTION = "Prepare an upgrade using a file on fs"

    @staticmethod
    def options(parser):
        parser.add_argument('--path', type=str, default=None,
                            required=True, help="FS path to upgrade image")
        parser.add_argument('--target', type=str, default='idle',
                            help='Target.  idle, prepare, arm.')

        # NB: This allows an unsafe upgrade, which can result in corruption if
        # used improperly. It should never be used on a production system.
        # It is useful when upgrading from a non-release build.
        parser.add_argument('--override-compatibility-check',
            action='store_true', default=False, help=argparse.SUPPRESS)

    @staticmethod
    def main(conninfo, credentials, args):
        target = convert_target(args.target)

        print upgrade.config_put(conninfo,
            credentials,
            args.path,
            target,
            args.override_compatibility_check)

class UpgradeError(Exception):
    pass

class UpgradeStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = "upgrade_status"
    DESCRIPTION = "List current upgrade status"

    @staticmethod
    def options(parser):
        parser.add_argument('--monitor', action="store_true",
            help='Monitor the status until PREPARING is completed.')

    @staticmethod
    def main(conninfo, credentials, args):
        repeat = True
        repeat_count = 0
        while repeat:
            # Timeout while PREPARING.
            if repeat_count > (5 * 60):
                raise UpgradeError("Preparing upgrade timed out.")

            repeat = False

            status = upgrade.status_get(conninfo, credentials)
            if args.monitor and status.lookup('state') == 'UPGRADE_PREPARING':
                repeat = True
                repeat_count += 1
                time.sleep(1)

        print status

        # Raise an error if monitoring for PREPARED and the final state was
        # different.
        if args.monitor and status.lookup('state') != 'UPGRADE_PREPARED':
            raise UpgradeError("Error preparing upgrade.")

