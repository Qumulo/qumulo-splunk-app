'''
Modular Input Script for Qumulo
'''

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


#set up logging
logging.root
logging.root.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s %(message)s')
#with zero args , should go to STD ERR
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.root.addHandler(handler)

SCHEME = """<scheme>
    <title>Qumulo</title>
    <description>Poll data from the Qumulo REST API</description>
    <use_external_validation>true</use_external_validation>
    <streaming_mode>xml</streaming_mode>
    <use_single_instance>true</use_single_instance>

    <endpoint>
        <args>
            <arg name="name">
                <title>Qumulo input name</title>
                <description>Name of this Qumulo input</description>
            </arg>

            <arg name="username">
                <title>Username</title>
                <description>username for authentication , defaults to admin</description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>true</required_on_create>
            </arg>
            <arg name="password">
                <title>Password</title>
                <description>password for authentication , defaults to admin</description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>true</required_on_create>
            </arg>
            <arg name="nodehost">
                <title>Host</title>
                <description>An ip address or hostname of a node in the cluster; use 'localhost' when running directly on the node</description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>true</required_on_create>
            </arg>
            <arg name="port">
                <title>Port</title>
                <description>port number for the API server port, defaults to 8000 </description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>true</required_on_create>
            </arg>

            <arg name="endpoint_to_poll">
                <title>Endpoint</title>
                <description>Qumulo REST endpoint to poll</description>
                <required_on_edit>true</required_on_edit>
                <required_on_create>true</required_on_create>
            </arg>

            <arg name="request_body">
                <title>Custom Request Body</title>
                <description>Request body payload for POST and PUT</description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>false</required_on_create>
            </arg>

            <arg name="request_headers">
                <title>Custom Request Headers</title>
                <description>in format prop=value,prop2=value2</description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>false</required_on_create>
            </arg>
            <arg name="request_url_args">
                <title>Custom Request URL Args</title>
                <description>in format arg=value,arg2=value2</description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>false</required_on_create>
            </arg>

            <arg name="polling_interval">
                <title>Polling Interval</title>
                <description>Interval time in seconds or a CRON pattern to poll the endpoint</description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>false</required_on_create>
            </arg>

            <arg name="delimiter">
                <title>Delimiter</title>
                <description>Delimiter to use for any multi "key=value" field inputs</description>
                <required_on_edit>false</required_on_edit>
                <required_on_create>false</required_on_create>
            </arg>

        </args>
    </endpoint>
</scheme>
"""

def get_current_datetime_for_cron():
    current_dt = datetime.now()
    #dont need seconds/micros for cron
    current_dt = current_dt.replace(second=0, microsecond=0)
    return current_dt

def process_throughput():
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
                print_xml_stream(json.dumps(log_entry))


def process_iops():

    try:
        iops = client.get_iops()

        for op in iops:
            print_xml_stream(json.dumps(op))

    except RequestError, excpt:
        logging.error("Exception performing request for IOPS: %s" % str(excpt))
        return

def process_capacity(client):
    try:
        capacity = client.get_capacity()
    except RequestError, excpt:
        logging.error("Exception performing request for Capacity: %s" % str(excpt))
        return

    cap = {}
    cap["free_gigabytes"] = int(long(float(capacity['free_size_bytes']))/math.pow(1024,3))
    cap["raw_gigabytes"] = int(long(float(capacity['raw_size_bytes']))/math.pow(1024,3))
    cap["total_gigabytes"] = int(long(float(capacity['total_size_bytes']))/math.pow(1024,3))
    print_xml_stream(json.dumps(cap))

# prints validation error data to be consumed by Splunk
def print_error(s):
    print "<error><message>%s</message></error>" % encodeXMLText(s)

# prints XML stream
def print_xml_stream(s):
    print "<stream><event unbroken=\"1\"><data>%s</data><done/></event></stream>" % encodeXMLText(s)

def encodeXMLText(text):
    text = text.replace("&", "&amp;")
    text = text.replace("\"", "&quot;")
    text = text.replace("'", "&apos;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace("\n", "")
    return text

def usage():
    print "usage: %s [--scheme|--validate-arguments]"
    logging.error("Incorrect Program Usage")
    sys.exit(2)

def do_scheme():
    print SCHEME

def validate_conf(config, key):
    if key not in config:
        raise Exception, "Invalid configuration received from Splunk: key '%s' is missing." % key

#read XML configuration passed from splunkd
def get_config():
    config = {}

    try:
        # read everything from stdin
        config_str = sys.stdin.read()

        # parse the config XML
        doc = xml.dom.minidom.parseString(config_str)
        root = doc.documentElement
        conf_node = root.getElementsByTagName("configuration")[0]
        if conf_node:
            logging.debug("XML: found configuration")
            stanza = conf_node.getElementsByTagName("stanza")[0]
            if stanza:
                stanza_name = stanza.getAttribute("name")
                if stanza_name:
                    logging.debug("XML: found stanza " + stanza_name)
                    config["name"] = stanza_name

                    params = stanza.getElementsByTagName("param")
                    for param in params:
                        param_name = param.getAttribute("name")
                        logging.debug("XML: found param '%s'" % param_name)
                        if param_name and param.firstChild and \
                           param.firstChild.nodeType == param.firstChild.TEXT_NODE:
                            data = param.firstChild.data
                            config[param_name] = data
                            logging.debug("XML: '%s' -> '%s'" % (param_name, data))

        checkpnt_node = root.getElementsByTagName("checkpoint_dir")[0]
        if checkpnt_node and checkpnt_node.firstChild and \
           checkpnt_node.firstChild.nodeType == checkpnt_node.firstChild.TEXT_NODE:
            config["checkpoint_dir"] = checkpnt_node.firstChild.data

        if not config:
            raise Exception, "Invalid configuration received from Splunk."

        # just some validation: make sure these keys are present (required)
    except Exception, e:
        raise Exception, "Error getting Splunk configuration via STDIN: %s" % str(e)

    return config

def validate_config(client):
    '''
    Validate that we have enough information to access the cluster before starting.
    At minimum a hostname must be provided.  We will default username, password
    and port number to use if not provided.  But all must be present after init.
    @param client:
    @return:
    '''
    # logging.error("validate_config: config is {0}".format(client.config))

    if not client.host:
        logging.error("validate_config: No host specified, existing....")
        sys.exit(1)

    try:
        client.login()
    except Exception,e:
      logging.error("validate_config: Invalid configuration specified: %s" % str(e))
      sys.exit(1)

def run(client):

    validate_config(client)

    #setup some globals
    global STANZA
    STANZA = config.get("name")

    #logical name of endpoint to poll
    # endpoint_to_poll=config.get("endpoint_to_poll","")
    # logging.error("In run method, endpoint to poll is : %s" % endpoint_to_poll)
    # if endpoint_to_poll == "":
    #     logging.error("No polling endpoint was specified , exiting.")
    #     sys.exit(2)

    process_capacity(client)
    return
    # try:

    #     if(endpoint_to_poll == "capacity"):
    #         process_capacity()
    #     elif(endpoint_to_poll == "iops"):
    #         process_iops()
    #     elif(endpoint_to_poll == "throughput"):
    #         process_throughput()

    #     # logging.error("polling type:%s endpoint:%s polling_interval:%s", polling_type, endpoint_to_poll, str(polling_interval))                

    # except RuntimeError,e:
    #     logging.error("Looks like an error: %s" % str(e))
    #     sys.exit(2)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "--scheme":
            do_scheme()
        elif sys.argv[1] == "--validate-arguments":
            print "Arguments are validated by logging in to cluster via API."
        elif sys.argv[1] == "--test":
            print 'No tests for the scheme present'
        else:
            print 'You giveth weird arguments'
    else:
        # off we go....
        config = get_config()
        client = QumuloClient(config)
        run(client)
    sys.exit(0)
