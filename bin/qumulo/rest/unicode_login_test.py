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

import qumulo.lib.opts
import qumulo.rest.ad

from qumulo.rest.rest_test_common import RestTest

import qinternal.check.pycheck as pycheck

class JoinAdUnicodeStringsRestTest(unittest.TestCase, RestTest):
    def setUp(self):
        # XXX sergio:
        # Re-factor this to use the "constructor" self.setUp
        RestTest.setUp(self, qumulo.rest.ad.join_ad, "POST")
        # Parameter strings
        # ASCII
        self.a_domain   = 'DOMAIN1'
        self.a_user     = 'user1'
        self.a_password = 'password1'
        self.a_ou       = 'ou1'
        self.a_netbios  = 'netbios'
        # Unicode
        self.u_domain   = u'DOMA\u00efN1'
        self.u_user     = u'\u0169ser1'
        self.u_password = u'passw\u014frd'
        self.u_ou       = u'\u014fu'
        self.u_netbios  = u'netbi\u014fs'

    def test_success_ascii(self):
        self.run_command(self.a_domain, self.a_user, self.a_password,
            self.a_ou, self.a_netbios)

        self.assertCalledWith('/v1/ad/join',
            body={
                'domain'          : self.a_domain,
                'user'            : self.a_user,
                'password'        : self.a_password,
                'ou'              : self.a_ou,
                'domain_netbios'  : self.a_netbios
            })

    def test_failure_unicode(self):
        # Unicode AD domain
        self.assert_request_raises(ValueError, domain=self.u_domain,
            username=self.a_user, password=self.a_password, ou=self.a_ou,
            domain_netbios=self.a_netbios)
        # Unicode username
        self.assert_request_raises(ValueError, domain=self.a_domain,
            username=self.u_user, password=self.a_password, ou=self.a_ou,
            domain_netbios=self.a_netbios)
        # Unicode password
        self.assert_request_raises(ValueError, domain=self.a_domain,
            username=self.a_user, password=self.u_password, ou=self.a_ou,
            domain_netbios=self.a_netbios)
        # Unicode Organizational Unit
        self.assert_request_raises(ValueError, domain=self.a_domain,
            username=self.a_user, password=self.a_password, ou=self.u_ou,
            domain_netbios=self.a_netbios)
        # Unicode NET BIOS domain
        self.assert_request_raises(ValueError, domain=self.a_domain,
            username=self.a_user, password=self.a_password, ou=self.a_ou,
            domain_netbios=self.u_netbios)

class LeaveAdUnicodeStringsRestTest(unittest.TestCase, RestTest):
    def setUp(self):
        RestTest.setUp(self, qumulo.rest.ad.leave_ad, "POST")
        # Parameter strings
        # ASCII
        self.a_domain   = 'DOMAIN1'
        self.a_user     = 'user1'
        self.a_password = 'password1'
        # Unicode
        self.u_domain   = u'DOMA\u00efN1'
        self.u_user     = u'\u0169ser1'
        self.u_password = u'passw\u014frd'

    def test_success_ascii(self):
        self.run_command(self.a_domain, self.a_user, self.a_password)

        self.assertCalledWith('/v1/ad/leave',
            body={
                'domain'          : self.a_domain,
                'user'            : self.a_user,
                'password'        : self.a_password
            })

    def test_failure_unicode(self):
        # Unicode AD domain
        self.assert_request_raises(ValueError, domain=self.u_domain,
            username=self.a_user, password=self.a_password)
        # Unicode username
        self.assert_request_raises(ValueError, domain=self.a_domain,
            username=self.u_user, password=self.a_password)
        # Unicode password
        self.assert_request_raises(ValueError, domain=self.a_domain,
            username=self.a_user, password=self.u_password)

if __name__ == '__main__':
    pycheck.main()
