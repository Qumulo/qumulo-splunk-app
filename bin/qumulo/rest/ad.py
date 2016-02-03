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

import qumulo.lib.request as request
import qumulo.lib.util as util

@request.request
def list_ad(conninfo, credentials):
    method = "GET"
    uri = "/v1/ad/status"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def poll_ad(conninfo, credentials):
    method = "GET"
    uri = "/v1/ad/monitor"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def join_ad(
        conninfo, credentials, domain, username, password, ou,
        domain_netbios=None):
    method = "POST"
    uri = "/v1/ad/join"

    if domain_netbios is None:
        domain_netbios = ""

    config = {
        "domain":         util.parse_ascii(domain, 'domain'),
        "domain_netbios": util.parse_ascii(domain_netbios, 'domain_netbios'),
        "user":           util.parse_ascii(username, 'username'),
        "password":       util.parse_ascii(password, 'password'),
        "ou":             util.parse_ascii(ou, 'ou')
    }

    return request.rest_request(conninfo, credentials, method, uri, body=config)

@request.request
def leave_ad(conninfo, credentials, domain, username, password):
    method = "POST"
    uri = "/v1/ad/leave"

    # XXX scott: support none for these in the api, also, don't call domain
    # assistant script in that case
    if username is None:
        username = ""
    if password is None:
        password = ""

    config = {
        "domain":   util.parse_ascii(domain, 'domain'),
        "user":     util.parse_ascii(username, 'username'),
        "password": util.parse_ascii(password, 'password')
    }

    return request.rest_request(conninfo, credentials, method, uri, body=config)

@request.request
def cancel_ad(conninfo, credentials):
    method = "POST"
    uri = "/v1/ad/cancel"

    return request.rest_request(conninfo, credentials, method, uri)
