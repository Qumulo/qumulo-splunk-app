# Copyright (c) 2012 Qumulo, Inc.
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
from qumulo.lib.uri import UriBuilder
from qumulo.rest import users

@request.request
def read_fs_stats(conninfo, credentials):
    method = "GET"
    uri = "/v1/file-system"
    return request.rest_request(conninfo, credentials, method, unicode(uri))

def format_output_acl(conninfo, credentials, rest_response):
    results, etag = rest_response
    try:
        def insert_trustee_details(ace):
            ace['trustee_details'], _etag = \
                users.unpack_identity(conninfo, credentials, ace['trustee'])
            return ace
        results['acl']['aces'] = \
            [insert_trustee_details(ace) for ace in results['acl']['aces']]
        return request.RestResponse(results, etag)
    except request.RequestError:
        # XXX ezra: Temporary hack to make upgrade tests work, until the
        # unpack_identity API goes into the upgrade baseline. See QFS-10814.
        return rest_response

@request.request
def set_acl(conninfo, credentials, path=None, id_=None, control=None,
            aces=None, if_match=None):

    if not control or not aces:
        raise ValueError("Must specify both control flags and ACEs")

    assert (path is not None) ^ (id_ is not None)
    ref = unicode(path) if path else unicode(id_)
    uri = build_files_uri([ref, "info", "acl"])

    control = list(control)
    aces = list(aces)
    if_match = None if not if_match else unicode(if_match)

    config = {'aces': aces, 'control': control}
    method = "PUT"

    return format_output_acl(conninfo, credentials, request.rest_request(
        conninfo, credentials, method, unicode(uri),
        body=config, if_match=if_match))

@request.request
def get_attr(conninfo, credentials, path=None, id_=None, snapshot=None):
    """
    This function is deprecated in favor of get_file_attr.
    """
    assert (path is not None) ^ (id_ is not None)
    ref = unicode(path) if path else unicode(id_)
    uri = build_files_uri([ref, "info", "attributes"])

    if snapshot:
        uri.add_query_param('snapshot', snapshot)

    method = "GET"
    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def set_attr(conninfo, credentials, mode, owner, group, size,
        modification_time, change_time, path=None, id_=None, if_match=None):
    """
    Sets all file attributes on the specified file system object.
    """
    assert (path is not None) ^ (id_ is not None)
    ref = unicode(path) if path else unicode(id_)
    uri = build_files_uri([ref, "info", "attributes"])
    if_match = None if not if_match else unicode(if_match)

    method = "PUT"

    config = {
        'mode': unicode(mode),
        'owner': unicode(owner),
        'group': unicode(group),
        'size': unicode(size),
        'modification_time': unicode(modification_time),
        'change_time': unicode(change_time),
    }
    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body=config, if_match=if_match)

@request.request
def get_file_attr(conninfo, credentials, id_=None, path=None, snapshot=None):
    assert (path is not None) ^ (id_ is not None)
    ref = unicode(path) if path else unicode(id_)
    uri = build_files_uri([ref, "info", "attributes"])

    if snapshot:
        uri.add_query_param('snapshot', snapshot)

    method = "GET"
    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def set_file_attr(conninfo, credentials, mode, owner, group, size,
        creation_time, modification_time, change_time, id_, if_match=None):
    """
    Updates select file attributes on the specified file system object.
    Attributes that are not to be updated should have None specified as
    their values.
    """
    uri = build_files_uri([id_, "info", "attributes"])
    if_match = None if not if_match else unicode(if_match)

    method = "PATCH"

    config = {}
    if mode:
        config['mode'] = unicode(mode)
    if owner:
        config['owner'] = unicode(owner)
    if group:
        config['group'] = unicode(group)
    if size:
        config['size'] = unicode(size)
    if creation_time:
        config['creation_time'] = unicode(creation_time)
    if modification_time:
        config['modification_time'] = \
            unicode(modification_time)
    if change_time:
        config['change_time'] = unicode(change_time)

    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body=config, if_match=if_match)

@request.request
def write_file(conninfo, credentials, data_file, path=None, id_=None,
       if_match=None):
    assert (path is not None) ^ (id_ is not None)
    ref = unicode(path) if path else unicode(id_)
    uri = build_files_uri([ref, "data"])
    if_match = None if not if_match else unicode(if_match)

    method = "PUT"
    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body_file=data_file, if_match=if_match,
        request_content_type=request.CONTENT_TYPE_BINARY)

@request.request
def get_acl(conninfo, credentials, path=None, id_=None, snapshot=None):
    assert (path is not None) ^ (id_ is not None)
    ref = unicode(path) if path else unicode(id_)
    uri = build_files_uri([ref, "info", "acl"])

    method = "GET"

    if snapshot:
        uri.add_query_param("snapshot", snapshot)

    return format_output_acl(conninfo, credentials, request.rest_request(
        conninfo, credentials, method, unicode(uri)))

# XXX michael: page_size should be an optional parameter to this function
@request.request
def read_directory(conninfo, credentials, page_size=None, path=None, id_=None,
        snapshot=None):
    '''
    @param {int} page_size  How many entries to return
    @param {str} path       Directory to read, by path
    @param {int} id_        Directory to read, by ID
    @param {int} snapshot   Snapshot ID of directory to read
    '''
    assert (path is not None) ^ (id_ is not None)

    # Ensure there is one trailing slash
    ref = unicode(path.rstrip('/') + '/') if path else unicode(id_)
    uri = build_files_uri([ref, "entries"]).append_slash()

    method = "GET"

    if page_size is not None:
        uri.add_query_param("limit", page_size)

    if snapshot:
        uri.add_query_param("snapshot", snapshot)

    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def read_file(conninfo, credentials, file_, path=None, id_=None, snapshot=None):
    assert (path is not None) ^ (id_ is not None)
    ref = unicode(path) if path else unicode(id_)
    uri = build_files_uri([ref, "data"])

    if snapshot:
        uri.add_query_param('snapshot', snapshot)

    method = "GET"
    return request.rest_request(conninfo, credentials, method, unicode(uri),
        response_content_type=request.CONTENT_TYPE_BINARY, response_file=file_)

@request.request
def create_file(conninfo, credentials, name, dir_path=None, dir_id=None):
    assert (dir_path is not None) ^ (dir_id is not None)
    ref = unicode(dir_path) if dir_path else unicode(dir_id)
    uri = build_files_uri([ref, "entries"]).append_slash()

    config = {
        'name': unicode(name).rstrip("/"),
        'action': 'CREATE_FILE'
    }

    method = "POST"
    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body=config)

@request.request
def create_directory(conninfo, credentials, name, dir_path=None, dir_id=None):
    assert (dir_path is not None) ^ (dir_id is not None)
    ref = unicode(dir_path) if dir_path else unicode(dir_id)
    uri = build_files_uri([ref, "entries"]).append_slash()

    config = {
        'name': unicode(name),
        'action': 'CREATE_DIRECTORY'
    }

    method = "POST"
    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body=config)

@request.request
def create_symlink(conninfo, credentials, name, target, dir_path=None,
                   dir_id=None, target_type=None):
    assert (dir_path is not None) ^ (dir_id is not None)
    ref = unicode(dir_path) if dir_path else unicode(dir_id)
    uri = build_files_uri([ref, "entries"]).append_slash()

    config = {
        'name': unicode(name).rstrip("/"),
        'old_path': unicode(target),
        'action': 'CREATE_SYMLINK'
    }
    if target_type is not None:
        config['symlink_target_type'] = target_type

    method = "POST"
    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body=config)

@request.request
def create_link(conninfo, credentials, name, target, dir_path=None,
                dir_id=None):
    assert (dir_path is not None) ^ (dir_id is not None)
    ref = unicode(dir_path) if dir_path else unicode(dir_id)
    uri = build_files_uri([ref, "entries"]).append_slash()

    config = {
        'name': unicode(name).rstrip("/"),
        'old_path': unicode(target),
        'action': 'CREATE_LINK'
    }

    method = "POST"
    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body=config)

@request.request
def rename(conninfo, credentials, name, source, dir_path=None, dir_id=None):
    assert (dir_path is not None) ^ (dir_id is not None)
    ref = unicode(dir_path) if dir_path else unicode(dir_id)
    uri = build_files_uri([ref, "entries"]).append_slash()

    config = {
        'name': unicode(name).rstrip("/"),
        'old_path': unicode(source),
        'action': 'RENAME'
    }

    method = "POST"
    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body=config)

@request.request
def delete(conninfo, credentials, path):
    method = "DELETE"
    uri = build_files_uri([unicode(path)])
    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def read_dir_aggregates(conninfo, credentials, path,
        recursive=False, max_entries=None, max_depth=None, order_by=None):
    method = "GET"
    path = unicode(path.rstrip('/') + '/')

    aggregate = "recursive-aggregates" if recursive else "aggregates"
    uri = build_files_uri([path, aggregate]).append_slash()

    method = "GET"
    if max_entries is not None:
        uri.add_query_param('max-entries', max_entries)
    if max_depth is not None:
        uri.add_query_param('max-depth', max_depth)
    if order_by is not None:
        uri.add_query_param('order-by', order_by)
    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def get_file_samples(conninfo, credentials, path, count, by_value):
    method = "GET"

    uri = build_files_uri([path, 'sample']).append_slash()
    uri.add_query_param('by-value', by_value)
    uri.add_query_param('limit', count)

    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def resolve_paths(conninfo, credentials, ids, snapshot=None):
    method = "POST"
    uri = build_files_uri(["resolve"])

    if snapshot:
        uri.add_query_param('snapshot', snapshot)

    return request.rest_request(
        conninfo, credentials, method, unicode(uri), body=ids)

#  _               _
# | |    ___   ___| | _____
# | |   / _ \ / __| |/ / __|
# | |__| (_) | (__|   <\__ \
# |_____\___/ \___|_|\_\___/
# FIGLET: Locks

VALID_LOCK_PROTO_TYPE_COMBINATIONS = [
    ('smb', 'byte-range'),
    ('smb', 'share-mode'),
    ('nlm', 'byte-range'),
]

@request.request
def list_locks_by_file(
        conninfo,
        credentials,
        protocol,
        lock_type,
        file_path=None,
        file_id=None,
        snapshot_id=None,
        limit=None,
        after=None):
    assert (protocol, lock_type) in VALID_LOCK_PROTO_TYPE_COMBINATIONS
    assert (file_path is not None) ^ (file_id is not None)
    ref = unicode(file_path) if file_path else unicode(file_id)
    uri = build_files_uri(
        [ref, 'locks', protocol, lock_type], append_slash = True)
    if limit:
        uri.add_query_param("limit", limit)
    if after:
        uri.add_query_param("after", after)
    if snapshot_id:
        uri.add_query_param("snapshot", snapshot_id)
    return request.rest_request(conninfo, credentials, "GET", unicode(uri))

@request.request
def list_locks_by_client(
        conninfo,
        credentials,
        protocol,
        lock_type,
        owner_name=None,
        owner_address=None,
        limit=None,
        after=None):
    assert (protocol, lock_type) in VALID_LOCK_PROTO_TYPE_COMBINATIONS
    uri = build_files_uri(['locks', protocol, lock_type], append_slash = True)
    if limit:
        uri.add_query_param("limit", limit)
    if after:
        uri.add_query_param("after", after)
    if owner_name:
        uri.add_query_param("owner_name", owner_name)
    if owner_address:
        uri.add_query_param("owner_address", owner_address)
    return request.rest_request(conninfo, credentials, "GET", unicode(uri))

def _get_remaining_pages(conninfo, credentials, result, limit):
    '''
    Given the first page of a lock grant listing, retrieves all subsequent
    pages, and returns the complete grant list.
    '''
    full_list = result.data['grants']
    while len(result.data['grants']) == limit:
        # If we got a full page, there are probably more pages.  Waiting for
        # an empty page would also be reasonable, but carries the risk of
        # never terminating if clients are frequently taking new locks.
        result = request.rest_request(
            conninfo, credentials, "GET", result.data['paging']['next'])
        full_list += result.data['grants']
    return full_list

@request.request
def list_all_locks_by_file(
        conninfo,
        credentials,
        protocol,
        lock_type,
        file_path=None,
        file_id=None,
        snapshot_id=None,
        limit=1000):
    '''
    Re-assembles the paginated list of lock grants for the given file.
    '''
    result = list_locks_by_file(conninfo, credentials, protocol, lock_type,
                                file_path, file_id, snapshot_id, limit)
    return _get_remaining_pages(conninfo, credentials, result, limit)

@request.request
def list_all_locks_by_client(
        conninfo,
        credentials,
        protocol,
        lock_type,
        owner_name=None,
        owner_address=None,
        limit=1000):
    '''
    Re-assembles the paginated list of lock grants for the given client.
    '''
    result = list_locks_by_client(conninfo, credentials, protocol, lock_type,
        owner_name, owner_address, limit)
    return _get_remaining_pages(conninfo, credentials, result, limit)

@request.request
def release_nlm_locks_by_client(
        conninfo,
        credentials,
        owner_name=None,
        owner_address=None):
    assert owner_name or owner_address
    protocol, lock_type = 'nlm', 'byte-range'
    uri = build_files_uri(['locks', protocol, lock_type], append_slash = True)
    if owner_name:
        uri.add_query_param("owner_name", owner_name)
    if owner_address:
        uri.add_query_param("owner_address", owner_address)
    return request.rest_request(conninfo, credentials, "DELETE", unicode(uri))

@request.request
def release_nlm_lock(
        conninfo,
        credentials,
        offset,
        size,
        owner_id,
        file_path=None,
        file_id=None,
        snapshot=None):
    assert (file_path is not None) ^ (file_id is not None)
    protocol, lock_type = 'nlm', 'byte-range'
    ref = unicode(file_path) if file_path else unicode(file_id)
    uri = build_files_uri(
            [ref, 'locks', protocol, lock_type], append_slash = True)
    uri.add_query_param("offset", offset)
    uri.add_query_param("size", size)
    uri.add_query_param("owner_id", owner_id)
    if snapshot is not None:
        uri.add_query_param("snapshot", snapshot)
    return request.rest_request(conninfo, credentials, "DELETE", unicode(uri))

#  _   _      _
# | | | | ___| |_ __   ___ _ __ ___
# | |_| |/ _ \ | '_ \ / _ \ '__/ __|
# |  _  |  __/ | |_) |  __/ |  \__ \
# |_| |_|\___|_| .__/ \___|_|  |___/
#              |_|
#
def build_files_uri(components, append_slash=False):
    uri = UriBuilder(path="/v1/files")

    if components:
        for component in components:
            uri.add_path_component(component)

    if append_slash:
        uri.append_slash()

    return uri

# Return an iterator that reads an entire directory. Each iteration returns a
# page of files, which will be the specified page size or less.
@request.request
def read_entire_directory(conninfo, credentials, page_size=None, path=None,
                          id_=None):
    # Perform initial read_directory normally.
    result = read_directory(conninfo, credentials, page_size=page_size,
        path=path, id_=id_)
    next_uri = result.data['paging']['next']
    yield result

    while next_uri != '':
        # Perform raw read_directory with paging URI.
        result = request.rest_request(conninfo, credentials, "GET", next_uri)
        next_uri = result.data['paging']['next']
        yield result

# Return an iterator that reads an entire directory. Each iteration returns a
# page of files. Any fs_no_such_entry_error returned is logged and ignored,
# ending the iteration.
def read_entire_directory_and_ignore_not_found(
    conninfo, credentials, page_size=None, path=None, id_=None):
    try:
        for result in read_entire_directory(
                conninfo, credentials, page_size, path, id_):
            yield result
    except request.RequestError as e:
        if e.status_code != 404 or e.error_class != 'fs_no_such_entry_error':
            raise

# Return an iterator that walks a file system tree depth-first and pre-order
@request.request
def tree_walk_preorder(conninfo, credentials, path):
    path = unicode(path)

    def call_read_dir(conninfo, credentials, path):
        for result in read_entire_directory_and_ignore_not_found(
                conninfo, credentials, path=path):
            if 'files' in result.data:
                for f in result.data['files']:
                    yield request.RestResponse(f, result.etag)

                    if f['type'] == 'FS_FILE_TYPE_DIRECTORY':
                        for ff in call_read_dir(conninfo, credentials,
                                                f['path']):
                            yield ff

    result = get_file_attr(conninfo, credentials, path=path)
    yield result

    for f in call_read_dir(conninfo, credentials, path):
        yield f

# Return an iterator that walks a file system tree depth-first and post-order
@request.request
def tree_walk_postorder(conninfo, credentials, path):
    path = unicode(path)

    def call_read_dir(conninfo, credentials, path):
        for result in read_entire_directory_and_ignore_not_found(
                conninfo, credentials, path=path):
            if 'files' in result.data:
                for f in result.data['files']:
                    if f['type'] == 'FS_FILE_TYPE_DIRECTORY':
                        for ff in call_read_dir(conninfo, credentials,
                                                f['path']):
                            yield ff
                    yield request.RestResponse(f, result.etag)

    result = get_file_attr(conninfo, credentials, path=path)

    for f in call_read_dir(conninfo, credentials, path):
        yield f

    yield result
