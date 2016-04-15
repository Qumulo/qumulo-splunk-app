import itertools
import json
import logging
import os
import sys
import time

import qumulo.lib.auth
import qumulo.lib.request
import qumulo.rest

import re
import os
import sys
import time
import random
from collections import OrderedDict
from qumulo.rest_client import RestClient


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

        self.username = config.get("username")
        self.password = config.get("password")
        self.host = config.get("nodehost")
        self.port = int(config.get("port", 8000))
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
            logging.error("Error logging in to the REST server %{0}: %{1}".format(self.host, excpt))
            # sys.exit(2)

    def path_to_paths(self, local_path):
        if local_path == "/" or local_path == "//" or local_path == "":
            return ['/']
        else:
            local_path = re.sub("//", "/", local_path)
            local_path = re.sub("/$", "", local_path)
        local_paths = []
        cur_path = ""
        for i_level, path_part in enumerate(local_path.split("/")):
            if i_level > 0:
                cur_path = cur_path + "/" + path_part
            if cur_path == "":
                cur_path = "/"
            local_paths.append(cur_path)
            if i_level == 0:
                cur_path = ""
        return local_paths

    def build_tree(self, iops_data, id_to_path, iops_dict, stop_level):
        new_big_tree = {}
        for d in iops_data['entries']:
            inode_id = int(d['id'])
            path = "/"
            try:
                for i, path in enumerate(self.path_to_paths(id_to_path[inode_id])):
                    if i not in new_big_tree:
                        new_big_tree[i] = {}
                    if path == "":
                        path = "/"
                    if path not in new_big_tree[i]:
                        new_big_tree[i][path] = iops_dict.copy()
                    new_big_tree[i][path]["path"] = path
                    new_big_tree[i][path]["counter"] += 1
                    new_big_tree[i][path][d["type"]] += d["rate"]
                    new_big_tree[i][path]["total"] += d["rate"]
                    new_big_tree[i][path][d["type"] + "-agg"] += d["rate"]
                    new_big_tree[i][path]["total-agg"] += d["rate"]
                    if i >= stop_level:
                        break
            except:
                pass
        return new_big_tree

    def get_api_response(self, api_call, **kwargs):

        attempt = 0
        response_object = None
        retry = True

        while retry and (attempt <= 10):
            try:
                if len(kwargs) > 0:
                    # TODO: fix.  This call is not really general-purpose yet
                    response_object = api_call(self.connection, self.credentials, kwargs.values()[0])
                else:
                    response_object = api_call(self.connection, self.credentials)

                if len(response_object) == 0:
                    retry = True
                else:
                    retry = False
            except Exception, excpt:

                if excpt.status_code == 401 or excpt.status_code == 307:
                     # is it a 307 or 401?  Try to get a new access token
                    # by logging in again
                    self.login()
                logging.error("Error communicating with Qumulo REST server: %s" % excpt)
                retry = True

        if retry:
            attempt += 1
            time.sleep(10)


        return response_object.data


    def get_capacity(self):
        # return qumulo.rest.fs.read_fs_stats(self.connection, self.credentials).data
        return self.get_api_response(qumulo.rest.fs.read_fs_stats)

    def peek(self, iterable):
        try:
            first = next(iterable)
        except StopIteration:
            return None
        return first, itertools.chain([first], iterable)

    def get_throughput(self):
        api_begin_time = int(time.time()-self.polling_interval)
        throughput = self.get_api_response(qumulo.rest.analytics.time_series_get, api_begin_time=api_begin_time)

        # return only the last/latest reading for each indicator... not all of them.
        if (throughput is None) or (self.peek(iter(throughput)) is None):
            return []

        results = []

        for result in throughput:
            if (("times" in result) and ("values" in result)) \
            and ((len(result["times"]) > 0) and (len(result["values"]))) > 0:
                result["times"] = [ result["times"][-1]]
                result["values"] = [ result["values"][-1]]
                results.append(result)

        return results

    def get_iops(self):

        # TODO:  Need better Map-Reduce code here.... check NumPY ufunc.reduce and friends http://goo.gl/xJYUnV
        iops_types = OrderedDict([("read","file_read"), ("write","file_write"), ("namespace-read","namespace_read"), ("namespace-write","namespace_write"), ("read-agg", ""), ("write-agg", ""), ("namespace-read-agg", ""), ("namespace-write-agg", "")])
        iops_dict = {"counter":0, "total":0, "total-agg":0}

        for c in iops_types:
            iops_dict[c] = 0

        big_tree = {}

        try:
            iops_data = self.get_api_response(qumulo.rest.analytics.iops_get)
            ids = {}

            for d in iops_data['entries']:
                inode_id = int(d['id'])
                if inode_id not in ids:
                    ids[inode_id] = 1

            # print "Get IDS"
            ids = sorted(ids.keys())
            id_to_path = {}

            while len(ids) > 0:
                fifty_ids = map(str, ids[:100])
                id_path_arr = self.get_api_response(qumulo.rest.fs.resolve_paths, ids=fifty_ids)
                for d in id_path_arr:
                    if int(d['id']) not in id_to_path:
                        id_to_path[int(d['id'])] = d['path']
                del ids[:100]

            raw = {}
            raw_only_dirs = {}
            ips = {}
            # print "Walk ip Entries"
            for d in iops_data['entries']:
                inode_id = int(d['id'])
                ip = d["ip"]
                if ip not in ips:
                    ips[ip] = iops_dict.copy()
                    ips[ip]["max-iops"] = 0
                    ips[ip]["max-path"] = ""

                ips[ip]["counter"] += 1
                ips[ip][d["type"]] += d["rate"]
                ips[ip]["total"] += d["rate"]
                try:
                    if ip + "\t" + id_to_path[inode_id] not in raw:
                        raw[ip + "\t" + id_to_path[inode_id]] = {"total":0, "read":0, "write":0, "namespace-read":0, "namespace-write":0}
                        raw[ip + "\t" + id_to_path[inode_id]]["total"] += d["rate"]
                        raw[ip + "\t" + id_to_path[inode_id]][d["type"]] += d["rate"]
                    short_path = re.sub("/[^/]*$", "", id_to_path[inode_id])
                    if ip + "\t" + short_path not in raw_only_dirs:
                        raw_only_dirs[ip + "\t" + short_path] = {"total":0, "read":0, "write":0, "namespace-read":0, "namespace-write":0}
                        raw_only_dirs[ip + "\t" + short_path]["total"] += d["rate"]
                        raw_only_dirs[ip + "\t" + short_path][d["type"]] += d["rate"]
                except:
                    pass

                if d["rate"] > ips[ip]["max-iops"]:
                    try:
                        ips[ip]["max-path"] = id_to_path[inode_id]
                    except:
                        pass
                    ips[ip]["max-iops"] = d["rate"]


            max_level_count = 5
            big_tree = self.build_tree(iops_data, id_to_path, iops_dict, max_level_count)

            # print "Build better tree"
            # 5 iops threshold
            thresh = 5
            for level in reversed(range(1,max_level_count+1)):
                removal_list = []
                for path in big_tree[level]:
                    d = big_tree[level][path]
                    if d["total"] > thresh:
                        #keeper, remove iops from parents. o(n^2) :-(
                        # print "Keeping: %s - %s" % (level, path)
                        for fix_level, fix_path in enumerate(self.path_to_paths(path)):
                            if fix_level < level:
                                for data_type in ["read", "namespace-read", "write", "namespace-write", "total"]:
                                    big_tree[fix_level][fix_path][data_type] -= d[data_type]
                    else:
                        #remove from the treee
                        removal_list.append(path)
                for path in removal_list:
                    # print "Deleting: %s - %s" % (level, path)
                    del big_tree[level][path]


            # print "Done"
        except:
            pass

        # sigh.... TODO: get rid of this
        results = []
        for key, value in big_tree.iteritems():
            if len(value.values()) > 0:
                dict = value.values()[0]
                results.append(dict)

        return results

