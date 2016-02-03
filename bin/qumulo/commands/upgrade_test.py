#!/usr/bin/env python
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

import json
import mock
import unittest

import qumulo.commands.upgrade as upgrade
import qumulo.lib.request as request

import qinternal.check.pycheck as pycheck

class UpgradeCommandTest(unittest.TestCase):
    def setUp(self):
        self.conninfo = mock.Mock()
        self.credentials = mock.Mock()
        self.args = mock.Mock()

    PREPARED_RESPONSE = '''
{
    "details": "",
    "install_path": "",
    "state": "UPGRADE_PREPARED"
}
'''

    IDLE_RESPONSE = '''
{
    "details": "",
    "install_path": "",
    "state": "UPGRADE_IDLE"
}
'''

    PREPARING_RESPONSE = '''
{
    "details": "",
    "install_path": "",
    "state": "UPGRADE_PREPARING"
}
'''

    @mock.patch('qumulo.rest.upgrade.status_get')
    def test_upgrade_status_monitor(self, status_get):
        status_get.return_value = request.RestResponse(
            json.loads(self.PREPARED_RESPONSE), '')
        setattr(self.args, 'monitor', True)
        upgrade.UpgradeStatusCommand.main(self.conninfo,
                self.credentials, self.args)

    @mock.patch('time.sleep')
    @mock.patch('qumulo.rest.upgrade.status_get')
    def test_upgrade_status_monitor_slow(self, status_get, _):
        # Return PREPARING 150x, then PREPARED
        status_get.side_effect = 150 * \
            [request.RestResponse(json.loads(self.PREPARING_RESPONSE), '')] + \
            [request.RestResponse(json.loads(self.PREPARED_RESPONSE), '')]

        setattr(self.args, 'monitor', True)
        upgrade.UpgradeStatusCommand.main(self.conninfo,
                self.credentials, self.args)

    @mock.patch('qumulo.rest.upgrade.status_get')
    def test_upgrade_status_monitor_idle(self, status_get):
        status_get.return_value = request.RestResponse(
            json.loads(self.IDLE_RESPONSE), '')
        setattr(self.args, 'monitor', True)

        with self.assertRaisesRegexp(
            upgrade.UpgradeError, "Error preparing upgrade."):
            upgrade.UpgradeStatusCommand.main(self.conninfo,
                self.credentials, self.args)

    @mock.patch('time.sleep')
    @mock.patch('qumulo.rest.upgrade.status_get')
    def test_upgrade_status_monitor_timeout(self, status_get, _):
        status_get.return_value = request.RestResponse(
            json.loads(self.PREPARING_RESPONSE), '')
        setattr(self.args, 'monitor', True)

        with self.assertRaisesRegexp(
            upgrade.UpgradeError, "Preparing upgrade timed out."):
            upgrade.UpgradeStatusCommand.main(self.conninfo,
                self.credentials, self.args)


if __name__ == '__main__':
    pycheck.main()
