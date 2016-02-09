'''
Modular Input Script for Qumulo
'''

import sys,logging,os,time,getopt
import xml.dom.minidom
from datetime import datetime

# qumulo_client wraps all of the Qumulo REST API interactions
from qumulo_client import QumuloClient

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
logging.root.setLevel(logging.ERROR)
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
    <use_single_instance>false</use_single_instance>

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
            
def do_validate():
    config = get_validation_config() 
    
    
def do_run(client):

    config = client.config

    #setup some globals
    global STANZA
    STANZA = config.get("name")
    

    #polling can be a time interval or CRON pattern
    # polling_interval_string = config.get("polling_interval","60")
    polling_interval_string = "60"
    
    if polling_interval_string.isdigit():
        polling_type = 'interval'
        # polling_interval=int(polling_interval_string)
        polling_interval = 60
    else:
        polling_type = 'cron'
        cron_start_date = datetime.now()
        cron_iter = croniter(polling_interval_string, cron_start_date)

    #optional custom fields
    delimiter=config.get("delimiter",",")

    try:
          
        while True:
             
            if polling_type == 'cron':
                next_cron_firing = cron_iter.get_next(datetime)
                while get_current_datetime_for_cron() != next_cron_firing:
                    time.sleep(float(10))
            
            print_xml_stream(client.get_iops())
            print_xml_stream(client.get_capacity())
            print_xml_stream(client.get_throughput())
            # based on value of endpoint_to_poll , execute the endpoint from the qumulo python API
            # get the JSON response
            # perform any processing on the response JSON
            # call the print_xml_stream function to write JSON out to Splunk

                #if(endpoint_to_poll == "stats"):
                    ## Obtain REST credentials
                #    (conninfo, creds) = login(host, username, password, port)
                #    ## Make the API call
                #    try:
                #        response, _  = qumulo.rest.stats.iops_get(
                #                conninfo, creds)
                #        print_xml_stream(response)
                #    except qumulo.lib.request.RequestError, excpt:
                #        logging.error("Exception performing request: %s" % str(excpt))
                #        continue


            if polling_type == 'interval':                         
                time.sleep(float(polling_interval))
            
    except RuntimeError,e:
        logging.error("Looks like an error: %s" % str(e))
        sys.exit(2) 
            

# prints validation error data to be consumed by Splunk
def print_validation_error(s):
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

#read XML configuration passed from splunkd, need to refactor to support single instance mode
def get_input_config():
    config = {}

    try:
        # read everything from stdin
        config_str = sys.stdin.read()

        # parse the config XML
        doc = xml.dom.minidom.parseString(config_str)
        root = doc.documentElement
        
        session_key_node = root.getElementsByTagName("session_key")[0]
        if session_key_node and session_key_node.firstChild and session_key_node.firstChild.nodeType == session_key_node.firstChild.TEXT_NODE:
            data = session_key_node.firstChild.data
            config["session_key"] = data 
            
        server_uri_node = root.getElementsByTagName("server_uri")[0]
        if server_uri_node and server_uri_node.firstChild and server_uri_node.firstChild.nodeType == server_uri_node.firstChild.TEXT_NODE:
            data = server_uri_node.firstChild.data
            config["server_uri"] = data   
            
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

        
    except Exception, e:
        raise Exception, "Error getting Splunk configuration via STDIN: %s" % str(e)

    return config

#read XML configuration passed from splunkd, need to refactor to support single instance mode
def get_validation_config():
    val_data = {}

    # read everything from stdin
    val_str = sys.stdin.read()

    # parse the validation XML
    doc = xml.dom.minidom.parseString(val_str)
    root = doc.documentElement

    logging.debug("XML: found items")
    item_node = root.getElementsByTagName("item")[0]
    if item_node:
        logging.debug("XML: found item")

        name = item_node.getAttribute("name")
        val_data["stanza"] = name

        params_node = item_node.getElementsByTagName("param")
        for param in params_node:
            name = param.getAttribute("name")
            logging.debug("Found param %s" % name)
            if name and param.firstChild and \
               param.firstChild.nodeType == param.firstChild.TEXT_NODE:
                val_data[name] = param.firstChild.data

    return val_data

if __name__ == '__main__':
      
    if len(sys.argv) > 1:
        if sys.argv[1] == "--scheme":           
            do_scheme()
        elif sys.argv[1] == "--validate-arguments":
            do_validate()
        else:
            usage()
    else:
        config = get_input_config()
        client = QumuloClient(config)
        do_run(client)

        
    sys.exit(0)
