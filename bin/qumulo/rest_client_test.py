#!/usr/bin/env python
# Copyright (c) 2014 Qumulo, Inc. All rights reserved.
#
# NOTICE: All information and intellectual property contained herein is the
# confidential property of Qumulo, Inc. Reproduction or dissemination of the
# information or intellectual property contained herein is strictly forbidden,
# unless separate prior written permission has been obtained from Qumulo, Inc.

import qpaths
qpaths.setpaths()

import collections
import mock
import os
import socket
import sys
import threading
import unittest

import tornado.httpserver
import tornado.ioloop
import tornado.web

import qinternal.check.port_allocator as port_allocator
import qinternal.check.pycheck as pycheck

# Tornado has philosophical differences with pylint
# pylint: disable=abstract-method,arguments-differ
# pylint: disable=attribute-defined-outside-init

ReturnValue = collections.namedtuple('ReturnValue', 'data etag')

# XXX philip: testing with global mutable state is always nassssty
def clean_global_rest_client_state():
    if 'cli.qumulo.rest_client' in sys.modules:
        del sys.modules['cli.qumulo.rest_client']

class PublicRestClientTests(unittest.TestCase):
    def setUp(self):
        clean_global_rest_client_state()

        from cli.qumulo.rest_client import RestClient
        self.rest_client_class = RestClient

    def test_has_no_private_module(self):
        # Do a spot test for a private module
        self.assertFalse(hasattr(self.rest_client_class, 'memory'))

    @unittest.skip('Is this really deprecated? Let MMurray know')
    def test_has_no_private_method(self):
        # fs public has no set attr; assert they're not here.
        r = self.rest_client_class('dummy', 42)
        self.assertFalse(hasattr(r.fs, 'set_attr'))

class RestClientTest(unittest.TestCase):
    '''
    A small test case to see that the property and request method creation
    functions are working as intended.
    '''
    def setUp(self):
        clean_global_rest_client_state()

        patcher = mock.patch('qumulo.rest.fs.create_link')
        self.addCleanup(patcher.stop)
        self.mock_create_link = patcher.start()
        self.mock_create_link.__name__ = 'create_link'
        self.mock_create_link.return_value = \
                ReturnValue({'key': 'value'}, 'md5')

        patcher = mock.patch('qumulo.rest.auth.login')
        self.addCleanup(patcher.stop)
        self.mock_login = patcher.start()
        self.mock_login.__name__ = 'login'
        self.mock_login.return_value = ReturnValue({
            'issue': 44,
            'key': 'key',
            'key_id': 'key_id',
            'algorithm': 'algorithm'
        }, 'etag')

        patcher = mock.patch('qumulo.lib.request.rest_request')
        self.addCleanup(patcher.stop)
        self.mock_rest_request = patcher.start()
        self.mock_rest_request.__name__ = 'rest_request'
        self.mock_rest_request.return_value = \
            ReturnValue({'fake': 'data'}, 'etag')

    def test_fs_create_link(self):
        import cli.qumulo.rest_client as rest_client
        rc = rest_client.RestClient('hostname', port=42)

        result = rc.fs.create_link('foo', 'bar', dir_id=97)
        self.mock_create_link.assert_called_once_with(
            rc.conninfo, rc.credentials, 'foo', 'bar', dir_id=97)

        self.assertEqual(result['key'], 'value')

        self.assertEqual([], self.mock_login.call_args_list)

    def test_with_login(self):
        import cli.qumulo.rest_client as rest_client
        rc = rest_client.RestClient('hostname', 1034)
        rc.login('user', 'pass')
        self.assertEqual(rc.credentials.issue, 44)

    def test_bare_request(self):
        import cli.qumulo.rest_client as rest_client
        rc = rest_client.RestClient('hostname', 1034)
        rc.request('GET', '/v1/session/login', body={'username': 'fake'})

        # Kind of a silly test, but the plumbing works.
        self.mock_rest_request.assert_called_once(rc.conninfo, rc.credentials,
            'GET', '/v1/session/login', body={'username': 'fake'})

    def test_rest_client_iterable(self):
        import cli.qumulo.rest_client as rest_client
        rc = rest_client.RestClient('hostname', 1034)

        def mondo_results():
            for i in range(3):
                yield ReturnValue({'i': i}, 'etag')

        self.mock_rest_request.return_value = mondo_results()
        results = rc.request('GET', '/v1/some_api', body={'something': 'fake'})

        # Prove that we're stripping the etag and returning an iterable.
        self.assertEqual([{'i': i} for i in range(3)], list(results))

class ImportTest(unittest.TestCase):
    '''
    Ensure the manually-maintained imports are complete.
    '''
    def setUp(self):
        clean_global_rest_client_state()

    def assert_imports(self, module):
        submodules = vars(module)
        for filename in os.listdir(os.path.dirname(module.__file__)):
            if filename.endswith('.py') and 'test' not in filename \
                    and filename != '__init__.py':
                self.assertIn(filename[:-3], submodules)

    def test_rest_imports_all(self):
        import cli.qumulo.rest as rest
        self.assert_imports(rest)

    def test_commands_imports_all(self):
        import cli.qumulo.commands as commands
        self.assert_imports(commands)

class FakeRestServer(object):
    def __init__(self, port, block):
        class Handler(tornado.web.RequestHandler):
            def initialize(self, response, block):
                self.response = response
                self.block = block

            def get(self, *args):
                if block:
                    block.wait()
                self.write(self.response)
                self.set_header('Content-Type', 'application/json')

        self.response = {u'hi': u'there'}
        app = tornado.web.Application([
            (r"/(.*)", Handler, { 'response': self.response, 'block': block})])
        src_root = qpaths.find_src_root()
        certfile = os.path.join(src_root, 'keys/eng.qumulo.com.crt')
        keyfile = os.path.join(src_root, 'keys/eng.qumulo.com.key')
        ssl_options = { "certfile": certfile, "keyfile": keyfile }
        server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_options)
        server.listen(port)
        self.io_loop = tornado.ioloop.IOLoop.instance()
        self.thread = threading.Thread(target=self.io_loop.start)
        self.thread.start()

    def stop(self):
        self.io_loop.stop()
        self.thread.join()

class FakeRestServerTest(unittest.TestCase):
    def setUp(self):
        clean_global_rest_client_state()

    def test_server(self):
        port = port_allocator.allocate_port(os.environ['TMPDIR'])
        server = FakeRestServer(port, None)

        import cli.qumulo.rest_client as rest_client
        rc = rest_client.RestClient('localhost', port=port)
        self.assertEqual(rc.version.version(), {u'hi': u'there'})

        server.stop()

class RestClientTimeoutTest(unittest.TestCase):
    '''
    Test cases to ensure the timeout functionality works as intended.
    '''
    def setUp(self):
        clean_global_rest_client_state()

    def test_connect_timeout(self):
        import cli.qumulo.rest_client as rest_client
        # Unreachable Test-Net ip from RFC-3330
        ipaddr = '192.0.2.1'
        rc = rest_client.RestClient(ipaddr, port=42, timeout=1)
        self.assertRaises(socket.timeout, rc.auth.login, 'admin', 'admin')

    def test_handshake_timeout(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = port_allocator.allocate_port(os.environ['TMPDIR'])
        server.bind(('localhost', port))
        server.listen(10)

        import cli.qumulo.rest_client as rest_client
        rc = rest_client.RestClient('localhost', port=port, timeout=1)
        self.assertRaisesRegexp(socket.error, r'timed out', rc.version.version)

    def test_read_timeout(self):
        port = port_allocator.allocate_port(os.environ['TMPDIR'])
        block = threading.Event()
        server = FakeRestServer(port, block)

        import cli.qumulo.rest_client as rest_client
        rc = rest_client.RestClient('localhost', port=port, timeout=1)
        self.assertRaisesRegexp(socket.error, r'timed out', rc.version.version)

        block.set()
        server.stop()

if __name__ == '__main__':
    pycheck.main()
