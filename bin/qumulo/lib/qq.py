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

import argparse
import os
import socket
import sys

import qumulo.lib.auth
import qumulo.lib.log as log
import qumulo.lib.opts as opts
import qumulo.lib.request

VERSION = 1.0

def main_options(parser):
    parser.add_argument("--chunked", action="store_true",
        default=qumulo.lib.request.DEFAULT_CHUNKED,
        help="Force chunked transfer encoding for requests")
    parser.add_argument("--chunk-size", type=int,
        default=qumulo.lib.request.DEFAULT_CHUNK_SIZE_BYTES,
        help=("Set chunk size in bytes for chunked "
              "transfer encoding (default: %d)" %
              qumulo.lib.request.DEFAULT_CHUNK_SIZE_BYTES))
    parser.add_argument("--credentials-store",
        default=qumulo.lib.auth.credential_store_filename(),
        help="Write credentials to a custom path")
    parser.add_argument("--debug", action="store_true", default=False)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--no-credentials", action="store_true",
        default=False, help=argparse.SUPPRESS)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("--version", action="version",
        version=("%(prog)s " + str(VERSION)))
    parser.add_argument("--timeout", type=int, default=None,
        help="Time (in seconds) to wait for response")

def main(args):
    if args.debug:
        log.set_debug()

    for _i in range(args.verbose):
        log.incr_verbosity()

    conninfo = qumulo.lib.request.Connection(
        args.host, args.port, chunked=args.chunked,
        chunk_size=args.chunk_size, timeout=args.timeout)

    credentials = qumulo.lib.auth.get_credentials(args.credentials_store)

    if args.request:
        args.request.main(conninfo, credentials, args)

def qq_main(argz=None):
    try:
        parzer = opts.ArgumentParserOverride(description="Qumulo CLI",
            add_help=True, prog=os.path.basename(sys.argv[0]))
        main_options(parzer)
        argz = opts.parse_options(parzer, sys.argv[1:])
        main(argz)
    except KeyboardInterrupt:
        print "\nCommand interrupted"
        return 1
    except qumulo.lib.request.RequestError, e:
        print e
        return 1
    except ValueError, e:
        if os.getenv("DEBUG_CLI") or (argz is not None and argz.debug):
            print "Command error: %s" % str(e)
            raise
        else:
            print "Command error: %s" % str(e)
            return 1
    except socket.error, e:
        print "Connection error: %s" % str(e)
        return 1

    return 0
