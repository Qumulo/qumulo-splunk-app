#!/usr/bin/env python
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

import unittest
import copy

import qumulo.lib.request as request
import qumulo.commands.fs

from qumulo.commands.test_mixin import CommandTest

import qinternal.check.pycheck as pycheck

class ReadDirectoryTest(unittest.TestCase, CommandTest):
    def setUp(self):
        CommandTest.setUp(self, qumulo.commands.fs.ReadDirectoryCommand,
            'fs_read_dir', 'qumulo.rest.fs.read_directory',
            'qumulo.lib.request.rest_request')

    def test_paginated_read(self):
        # mock out response that requires more pages (actual JSON content
        # is otherwise irrelevant here)
        paging_response = {
            'paging': {'next': '/v1/something' },
            'files': ['foobar'],
            'path': '/'
        }
        self.mock.read_directory.return_value = \
            request.RestResponse(paging_response, 'etag-1')

        # mock out final response where next is empty
        last_response = copy.deepcopy(paging_response)
        last_response['paging']['next'] = ''
        self.mock.rest_request.return_value = \
            request.RestResponse(last_response, 'etag-2')

        # call should make both calls and print both responses
        expected = request.pretty_json(paging_response) + '\n' + \
                request.pretty_json(last_response) + '\n'
        self.assert_command_outputs(expected, '--path', '/', '--page-size', '2')

if __name__ == '__main__':
    pycheck.main()
