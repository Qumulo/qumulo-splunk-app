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

import qumulo.lib.request as request

@request.request
def get_block_settings(conninfo, credentials):
    method = "GET"
    uri = "/v1/debug/block/settings"
    return request.rest_request(conninfo, credentials, method, uri)

# pylint: disable=unused-argument
@request.request
def set_block_settings(conninfo, credentials,
        expiration_pct=None, max_checkpoints=None, max_expires=None,
        max_prefetches=None, target_wal_length=None, es_gen_bump_pct=None,
        es_catch_up_pct=None):

    method = "PATCH"
    uri = "/v1/debug/block/settings"

    config = {}
    for field in ['expiration_pct', 'max_checkpoints', 'max_expires',
                  'max_prefetches', 'target_wal_length', 'es_gen_bump_pct',
                  'es_catch_up_pct']:
        value = locals().get(field)
        if value is not None:
            # these asserts done because of integer/unsigned mismatch python/c
            # all settings are unsigned
            assert value >= 0
            config[field] = value

    return request.rest_request(conninfo, credentials, method, uri, body=config)
