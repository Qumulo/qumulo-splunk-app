import json
import logging
import os
import sys
import time

import qumulo.lib.auth
import qumulo.lib.request
import qumulo.rest


class QumuloClient(object):
    ''' class wrapper for REST API cmd so that we can new them up in tests '''
    def __init__(self, config):

        #set up logging
        logging.root
        logging.root.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(levelname)s %(message)s')
        #with zero args , should go to STD ERR
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)

        self.username = config.get("username","admin")
        self.password = config.get("password","admin")
        self.host = config.get("nodehost","gravytrain")
        self.port = int(config.get("port",8000))
        # self.polling_interval = int(config.get("polling_interval",60))
        self.polling_interval = 60
        self.connection = None
        self.credentials = None
        self.config = config

        self.login()

    def login(self):
        try:
            self.connection = qumulo.lib.request.Connection(self.host, self.port)
            login_results, _ = qumulo.rest.auth.login(\
                    self.connection, None, self.username, self.password)

            self.credentials = qumulo.lib.auth.Credentials.\
                    from_login_response(login_results)
        except Exception, excpt:
            logging.error("Error connecting to the REST server: %s" % excpt)
            sys.exit(2)


    def get_capacity(self):
        return qumulo.rest.fs.read_fs_stats(self.connection, self.credentials).data

    def get_iops(self):
        return qumulo.rest.analytics.iops_get(self.connection, self.credentials).data

    def get_throughput(self):
        api_begin_time = int(time.time()-self.polling_interval)
        return qumulo.rest.analytics.time_series_get(self.connection, self.credentials, api_begin_time).data

