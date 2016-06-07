#!/usr/bin/env python
#
# Copyright 2016 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from datetime import datetime
import json
import math
import os
import sys
import logging
import time
import xml.dom.minidom

#  qumulo_client wraps all of the Qumulo REST API interactions
from qumulo_client import QumuloClient
from qumulo.lib.request import RequestError


SPLUNK_HOME = os.environ.get("SPLUNK_HOME")
STANZA = None
EGG_DIR = SPLUNK_HOME + "/etc/apps/qumulo_splunk_app/bin/"

# Import any Eggs
for filename in os.listdir(EGG_DIR):
    if filename.endswith(".egg"):
        sys.path.append(EGG_DIR + filename)

from croniter import croniter


from splunklib.modularinput import *

class QumuloScript(Script):
    """All modular inputs should inherit from the abstract base class Script
    from splunklib.modularinput.script.
    They must override the get_scheme and stream_events functions, and,
    if the scheme returned by get_scheme has Scheme.use_external_validation
    set to True, the validate_input function.
    """
    def get_scheme(self):
        """When Splunk starts, it looks for all the modular inputs defined by
        its configuration, and tries to run them with the argument --scheme.
        Splunkd expects the modular inputs to print a description of the
        input in XML on stdout. The modular input framework takes care of all
        the details of formatting XML and printing it. The user need only
        override get_scheme and return a new Scheme object.

        :return: scheme, a Scheme object
        """
        # "random_numbers" is the name Splunk will display to users for this input.
        scheme = Scheme("Qumulo Splunk App")

        scheme.description = "Manage Qumulo Clusters using Splunk."
        # If you set external validation to True, without overriding validate_input,
        # the script will accept anything as valid. Generally you only need external
        # validation if there are relationships you must maintain among the
        # parameters, such as requiring min to be less than max in this example,
        # or you need to check that some resource is reachable or valid.
        # Otherwise, Splunk lets you specify a validation string for each argument
        # and will run validation internally using that string.
        scheme.use_external_validation = True
        scheme.use_single_instance = False

        username_argument = Argument("username")
        username_argument.title = "Username"
        username_argument.data_type = Argument.data_type_string
        username_argument.description = "Username for authentication , defaults to admin"
        username_argument.required_on_create = True
        username_argument.required_on_edit = False
        # If you are not using external validation, you would add something like:
        #
        # scheme.validation = "min > 0"
        scheme.add_argument(username_argument)

        password_argument = Argument("password")
        password_argument.title = "Password"
        password_argument.data_type = Argument.data_type_string
        password_argument.description = "Password for authentication , defaults to admin"
        password_argument.required_on_create = True
        password_argument.required_on_edit = False
        scheme.add_argument(password_argument)

        nodehost_argument = Argument("nodehost")
        nodehost_argument.title = "Host"
        nodehost_argument.data_type = Argument.data_type_string
        nodehost_argument.description = "Cluster hostname or IP address"
        nodehost_argument.required_on_create = True
        nodehost_argument.required_on_edit = False
        scheme.add_argument(nodehost_argument)

        port_argument = Argument("port")
        port_argument.title = "Port"
        port_argument.data_type = Argument.data_type_number
        port_argument.description = "Port number for Cluster API access, defaults to 8000"
        port_argument.required_on_create = True
        port_argument.required_on_edit = False
        scheme.add_argument(port_argument)

        return scheme

    def validate_input(self, validation_definition):
        """In this example we are using external validation to verify that min is
        less than max. If validate_input does not raise an Exception, the input is
        assumed to be valid. Otherwise it prints the exception as an error message
        when telling splunkd that the configuration is invalid.

        When using external validation, after splunkd calls the modular input with
        --scheme to get a scheme, it calls it again with --validate-arguments for
        each instance of the modular input in its configuration files, feeding XML
        on stdin to the modular input to do validation. It is called the same way
        whenever a modular input's configuration is edited.

        :param validation_definition: a ValidationDefinition object
        """
        # Get the parameters from the ValidationDefinition object,
        # then typecast the values as floats
        pass
 
    def stream_events(self, inputs, ew):
        """This function handles all the action: splunk calls this modular input
        without arguments, streams XML describing the inputs to stdin, and waits
        for XML on stdout describing events.

        If you set use_single_instance to True on the scheme in get_scheme, it
        will pass all the instances of this input to a single instance of this
        script.

        :param inputs: an InputDefinition object
        :param ew: an EventWriter object
        """

        # Go through each input for this modular input
        for input_name, input_item in inputs.inputs.iteritems():

            if input_item['username'] is not None:
                # Create a Qumulo client
                client = QumuloClient(input_item)

                if input_item["endpoint_to_poll"] == "throughput":
                    result = self.process_throughput(ew, input_name, client)
                elif input_item["endpoint_to_poll"] == "capacity":
                    result = self.process_capacity(ew, input_name, client)
                elif input_item["endpoint_to_poll"] == "iops":
                    result = self.process_iops(ew, input_name, client)

    def process_iops(self, ew, input_name, client):

        try:
            iops = client.get_iops()

            for op in iops:
                # print_xml_stream(json.dumps(op))
                # Create an Event object, and set its data fields
                event = Event()
                event.stanza = input_name
                event.data = json.dumps(op)
                ew.write_event(event)

        except RequestError, excpt:
            logging.error("Exception performing request for IOPS: %s" % str(excpt))
            return

    def process_capacity(self, ew, input_name, client):
        try:
            capacity = client.get_capacity()
        except RequestError, excpt:
            logging.error("Exception performing request for Capacity: %s" % str(excpt))
            return

        cap = {}
        cap["free_gigabytes"] = int(long(float(capacity['free_size_bytes']))/math.pow(1024,3))
        cap["raw_gigabytes"] = int(long(float(capacity['raw_size_bytes']))/math.pow(1024,3))
        cap["total_gigabytes"] = int(long(float(capacity['total_size_bytes']))/math.pow(1024,3))
        # print_xml_stream(json.dumps(cap))
        event = Event()
        event.stanza = input_name
        event.data = json.dumps(cap)
        ew.write_event(event)

    def process_throughput(self, ew, input_name, client):
        try:
            throughput = client.get_throughput()
        except RequestError, excpt:
            logging.error("Exception performing request for Throughput: %s" % str(excpt))
            return

        for entry in throughput:
            for i in range(len(entry['values'])):
                log_entry = {}
                if "throughput" in entry['id']:
                    log_entry['metric'] = entry['id']
                    log_entry['time'] = entry['times'][i]
                    log_entry['value'] = entry['values'][i]
                    # print_xml_stream(json.dumps(log_entry))
                    event = Event()
                    event.stanza = input_name
                    event.data = json.dumps(log_entry)
                    ew.write_event(event)







if __name__ == "__main__":
    sys.exit(QumuloScript().run(sys.argv))
