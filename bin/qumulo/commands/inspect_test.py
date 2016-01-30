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

import unittest
import qumulo.lib.request as request
import qumulo.commands.inspect
from qumulo.commands.test_mixin import CommandTest

import qinternal.check.pycheck as pycheck

class VerifyTest(unittest.TestCase, CommandTest):
    def setUp(self):
        CommandTest.setUp(
            self, qumulo.commands.inspect.InspectVerifyOfflinePostCommand,
            'verify_offline',
            'qumulo.rest.inspect.verify_offline')

    def test_verify_offline_corruption_found(self):
        fake_response = {
            'success': False,
            'status_string': 'Fake corruption'
        }
        self.mock.verify_offline.return_value = \
            request.RestResponse(fake_response, '')

        self.assert_exit_regexp('Corruption found:\nFake corruption')

    def test_verify_offline_no_corruption_found(self):
        fake_response = {
            'success': True,
            'status_string': ''
        }
        self.mock.verify_offline.return_value = \
            request.RestResponse(fake_response, '')

        self.assert_command_outputs('Verifying filesystem...\nFilesystem ok.\n')

if __name__ == '__main__':
    pycheck.main()
