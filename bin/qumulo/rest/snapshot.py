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

import qumulo.lib.request as request

@request.request
def create_snapshot(conninfo, credentials, name=None):
    method = 'POST'
    uri = '/v1/snapshots/'

    # Name is an optional parameter
    snapshot = {}
    if name:
        snapshot['name'] = name

    return request.rest_request(conninfo, credentials, method, uri,
        body=snapshot)

@request.request
def list_snapshots(conninfo, credentials):
    method = 'GET'
    uri = '/v1/snapshots/'

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def list_snapshot(conninfo, credentials, snapshot_id):
    method = 'GET'
    uri = '/v1/snapshots/{}'

    return request.rest_request(conninfo, credentials, method,
        uri.format(snapshot_id))

@request.request
def delete_snapshot(conninfo, credentials, snapshot_id):
    method = 'DELETE'
    uri = '/v1/snapshots/{}'

    return request.rest_request(conninfo, credentials, method,
        uri.format(snapshot_id))
